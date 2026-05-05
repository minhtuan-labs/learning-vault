from __future__ import annotations

import json
from datetime import datetime

from app.core.config import settings
from app.db.base import SessionLocal
from app.models.ai_analysis import AIAnalysis
from app.models.company import Company
from app.models.financial import FinancialData, FinancialPeriod
from app.services.financial_data_extractor import _BANK_KEYWORDS, _is_bank


class AIAnalyzer:
    def __init__(self):
        self.api_key = settings.claude_api_key
        self.model = settings.claude_model

    def _get_period_metrics(self, db, period_id: int) -> dict[str, float]:
        rows = db.execute(
            FinancialData.__table__.select().where(FinancialData.period_id == period_id)
        ).all()
        return {row.metric_name: float(row.metric_value) for row in rows}

    def _metrics_to_text(self, metrics: dict[str, float], label: str) -> str:
        lines = [f"--- {label} ---"]
        for name, value in metrics.items():
            lines.append(f"  {name}: {value:,.0f}")
        return "\n".join(lines)

    def analyze_period(self, period_id: int) -> str:
        db = SessionLocal()
        try:
            period = db.get(FinancialPeriod, period_id)
            if not period:
                return ""

            company = db.get(Company, period.company_id)
            if not company:
                return ""

            is_bank_entity = _is_bank(company.industry)

            current_metrics = self._get_period_metrics(db, period_id)

            prev_stmt = (
                db.query(FinancialPeriod)
                .filter(
                    FinancialPeriod.company_id == period.company_id,
                    FinancialPeriod.period_type == period.period_type,
                )
                .order_by(FinancialPeriod.year.desc(), FinancialPeriod.quarter.desc())
                .all()
            )
            prev_period = None
            for p in prev_stmt:
                if p.id != period.id:
                    prev_period = p
                    break

            prev_metrics = {}
            if prev_period:
                prev_metrics = self._get_period_metrics(db, prev_period.id)

            period_label = f"Q{period.quarter}/{period.year}" if period.quarter else f"Năm {period.year}"

            prompt = f"""Bạn là chuyên gia phân tích tài chính. Dựa trên số liệu BCTC sau, hãy viết nhận xét tổng quan (200-300 từ) về tình hình kinh doanh của doanh nghiệp trong kỳ này.

Doanh nghiệp: {company.name} ({company.code})
Kỳ báo cáo: {period_label}
Loại hình: {"Ngân hàng" if is_bank_entity else "Doanh nghiệp thường"}

{self._metrics_to_text(current_metrics, "Số liệu kỳ này")}

{self._metrics_to_text(prev_metrics, "Số liệu kỳ trước") if prev_metrics else "Không có số liệu kỳ trước để so sánh."}

Yêu cầu:
- Đề cập: điểm tích cực, điểm cần lưu ý, so sánh kỳ trước (nếu có)
- Ngôn ngữ: Tiếng Việt, dễ hiểu, không dùng thuật ngữ quá chuyên sâu
- Viết dưới dạng đoạn văn (prose), không dùng bullet points
- Độ dài: 200-300 từ
"""

            if not self.api_key:
                return f"[Mô phỏng AI] Phân tích tình hình kinh doanh kỳ {period_label} của {company.name}..."

            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            analysis_text = response.content[0].text.strip()

            analysis = AIAnalysis(
                company_id=period.company_id,
                period_id=period_id,
                analysis_text=analysis_text,
                analysis_html="",
                created_at=datetime.now(),
            )
            db.add(analysis)
            db.commit()

            return analysis_text

        except Exception as e:
            print(f"AI analysis error: {e}")
            return ""
        finally:
            db.close()

    def analyze_comparison(self, company_ids: list[int], year: int, quarter: int | None) -> str:
        db = SessionLocal()
        try:
            companies = db.query(Company).filter(Company.id.in_(company_ids)).all()
            if not companies:
                return ""

            period_data = {}
            for c in companies:
                period = (
                    db.query(FinancialPeriod)
                    .filter(
                        FinancialPeriod.company_id == c.id,
                        FinancialPeriod.year == year,
                        FinancialPeriod.quarter == quarter,
                    )
                    .first()
                )
                if period:
                    metrics = self._get_period_metrics(db, period.id)
                    period_data[c.code] = {
                        "name": c.name,
                        "metrics": metrics,
                        "period_label": f"Q{quarter}/{year}" if quarter else f"Năm {year}",
                    }

            if not period_data:
                return "Không có dữ liệu để so sánh."

            prompt = f"""Bạn là chuyên gia phân tích tài chính. Hãy so sánh tình hình kinh doanh của các doanh nghiệp sau trong kỳ {f"Quý {quarter}/{year}" if quarter else f"Năm {year}"}.

"""
            for code, data in period_data.items():
                prompt += f"\n{code} - {data['name']}:\n"
                prompt += self._metrics_to_text(data["metrics"], "Số liệu") + "\n"

            prompt += """
Yêu cầu:
- Nhận xét so sánh từng doanh nghiệp
- Chỉ ra DN có kết quả tốt nhất, cần lưu ý nhất
- Ngôn ngữ: Tiếng Việt, dễ hiểu
- Viết dưới dạng đoạn văn (prose), không dùng bullet points
- Độ dài: 300-400 từ
"""

            if not self.api_key:
                return f"[Mô phỏng AI] So sánh {len(period_data)} doanh nghiệp kỳ {year}..."

            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"AI comparison error: {e}")
            return ""
        finally:
            db.close()
