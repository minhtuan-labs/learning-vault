from __future__ import annotations

from datetime import datetime, timezone

import markdown_it
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.company import Company
from app.models.financial import FinancialData, FinancialPeriod
from app.models.summary import CompanySummary

_SYSTEM_PROMPT = """Bạn là chuyên gia phân tích tài chính Việt Nam. Nhiệm vụ: tóm tắt tình hình kinh doanh của doanh nghiệp dựa trên dữ liệu tài chính được cung cấp.

Yêu cầu:
- Viết bằng tiếng Việt, rõ ràng, súc tích (4–6 đoạn ngắn).
- Đánh giá xu hướng doanh thu và lợi nhuận theo thời gian.
- Nhận xét về các chỉ số tài chính quan trọng (ROE, ROA, biên lợi nhuận, dòng tiền...).
- Chỉ ra điểm mạnh và điểm cần lưu ý.
- Kết luận ngắn về tình hình chung.
- Chỉ dùng số liệu được cung cấp, không bịa đặt."""

_MAX_PERIODS = 12


class SummaryService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, company_id: int) -> CompanySummary | None:
        return self.db.scalar(
            select(CompanySummary).where(CompanySummary.company_id == company_id)
        )

    def generate_and_save(self, company_id: int) -> CompanySummary:
        if not settings.anthropic_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chưa cấu hình ANTHROPIC_API_KEY.",
            )

        company = self.db.get(Company, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy doanh nghiệp.",
            )

        context = self._build_context(company)
        summary_text = self._call_claude(context)
        md = markdown_it.MarkdownIt("commonmark", {"breaks": True, "html": True})
        md.enable(["table", "fence"])
        summary_html = md.render(summary_text)

        existing = self.get_summary(company_id)
        if existing:
            existing.summary_text = summary_text
            existing.summary_html = summary_html
            existing.generated_at = datetime.now(timezone.utc)
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        record = CompanySummary(company_id=company_id, summary_text=summary_text, summary_html=summary_html)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def _build_context(self, company: Company) -> str:
        periods = list(
            self.db.scalars(
                select(FinancialPeriod)
                .where(FinancialPeriod.company_id == company.id)
                .order_by(FinancialPeriod.year, FinancialPeriod.quarter)
            ).all()
        )
        # Keep only the most recent N periods to stay within context limits
        periods = periods[-_MAX_PERIODS:]

        lines: list[str] = [
            f"Doanh nghiệp: {company.name} ({company.code})",
            f"Sàn niêm yết: {company.exchange.value}",
        ]
        if company.industry:
            lines.append(f"Ngành: {company.industry}")
        lines.append("")

        for p in periods:
            label = (
                f"Năm {p.year}"
                if p.period_type.value == "Y"
                else f"Quý {p.quarter}/{p.year}"
            )
            lines.append(f"=== {label} ===")

            data_rows = list(
                self.db.scalars(
                    select(FinancialData).where(FinancialData.period_id == p.id)
                ).all()
            )

            if not data_rows:
                lines.append("(Chưa có dữ liệu tài chính)")
            else:
                for row in data_rows:
                    lines.append(f"- {row.metric_name}: {float(row.metric_value):,.2f} {row.unit}")
            lines.append("")

        return "\n".join(lines)

    def _call_claude(self, context: str) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        try:
            message = client.messages.create(
                model=settings.anthropic_model,
                max_tokens=2048,
                system=_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Hãy tóm tắt tình hình kinh doanh dựa trên dữ liệu sau:\n\n{context}",
                    }
                ],
            )
        except Exception as e:
            err = str(e)
            fallback = "claude-sonnet-4-6"
            if "not_found_error" in err and "model" in err.lower() and settings.anthropic_model != fallback:
                message = client.messages.create(
                    model=fallback,
                    max_tokens=2048,
                    system=_SYSTEM_PROMPT,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Hãy tóm tắt tình hình kinh doanh dựa trên dữ liệu sau:\n\n{context}",
                        }
                    ],
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Lỗi khi gọi AI: {e!s}",
                ) from e

        return "".join(block.text for block in message.content if block.type == "text")
