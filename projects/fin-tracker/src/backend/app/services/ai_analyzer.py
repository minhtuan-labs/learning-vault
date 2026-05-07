from __future__ import annotations

import json
import logging
from datetime import datetime

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.ai_analysis import AIAnalysis, AnalysisStatus
from app.models.company import Company
from app.models.financial import FinancialData, FinancialPeriod
from app.services.pdf_extractor import BANK_KEYWORDS, _is_bank

logger = logging.getLogger(__name__)


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

    def analyze_company(self, company_id: int, period_limit: int = 4) -> str:
        """Generate one analysis per company based on recent periods."""
        db = SessionLocal()
        try:
            company = db.get(Company, company_id)
            if not company:
                return ""

            is_bank_entity = _is_bank(company.industry)

            # Get all periods sorted by: year desc, quarter desc (quarterly before yearly for same year)
            all_periods = (
                db.query(FinancialPeriod)
                .filter(FinancialPeriod.company_id == company_id)
                .order_by(FinancialPeriod.year.desc(), FinancialPeriod.quarter.desc())
                .all()
            )

            if not all_periods:
                return ""

            # Build recent periods: pick the latest period for each year
            # For each year, prefer quarterly (latest quarter) over yearly
            seen_years = set()
            recent_periods = []
            for p in all_periods:
                if p.year not in seen_years:
                    recent_periods.append(p)
                    seen_years.add(p.year)
                    if len(recent_periods) >= period_limit:
                        break

            # Sort by year desc, quarter desc for consistent output
            recent_periods.sort(key=lambda p: (-p.year, -(p.quarter or 0)))

            if not recent_periods:
                return ""

            # Build metrics text for recent periods
            periods_text = ""
            for p in recent_periods:
                metrics = self._get_period_metrics(db, p.id)
                label = f"Q{p.quarter}/{p.year}" if p.quarter else f"Năm {p.year}"
                periods_text += self._metrics_to_text(metrics, label) + "\n\n"

            # Get older periods for comparison
            oldest_year_in_recent = min(p.year for p in recent_periods)
            prev_periods = (
                db.query(FinancialPeriod)
                .filter(
                    FinancialPeriod.company_id == company_id,
                    FinancialPeriod.year < oldest_year_in_recent,
                )
                .order_by(FinancialPeriod.year.desc(), FinancialPeriod.quarter.desc())
                .limit(2)
                .all()
            )

            prev_text = ""
            if prev_periods:
                for p in prev_periods:
                    metrics = self._get_period_metrics(db, p.id)
                    label = f"Q{p.quarter}/{p.year}" if p.quarter else f"Năm {p.year}"
                    prev_text += self._metrics_to_text(metrics, label) + "\n\n"
            else:
                prev_text = "Không có số liệu kỳ trước để so sánh."

            latest_label = f"Q{recent_periods[0].quarter}/{recent_periods[0].year}" if recent_periods[0].quarter else f"Năm {recent_periods[0].year}"

            prompt = f"""Bạn là chuyên gia phân tích tài chính. Dựa trên số liệu BCTC gần đây sau, hãy viết nhận xét tổng quan (300-400 từ) về tình hình kinh doanh của doanh nghiệp.

Doanh nghiệp: {company.name} ({company.code})
Kỳ phân tích chính: {latest_label}
Loại hình: {"Ngân hàng" if is_bank_entity else "Doanh nghiệp thường"}

{periods_text}
Số liệu kỳ trước (để so sánh):
{prev_text}
Yêu cầu:
- Đề cập: điểm tích cực, điểm cần lưu ý, xu hướng qua các kỳ gần đây
- So sánh với kỳ trước (nếu có)
- Ngôn ngữ: Tiếng Việt, dễ hiểu, không dùng thuật ngữ quá chuyên sâu
- Viết dưới dạng đoạn văn (prose), không dùng bullet points
- Độ dài: 300-400 từ
"""

            if not self.api_key:
                return f"[Mô phỏng AI] Phân tích tình hình kinh doanh của {company.name}..."

            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )

            analysis_text = response.content[0].text.strip()

            # Convert markdown to HTML
            import markdown_it
            md = markdown_it.MarkdownIt("commonmark", {"breaks": True, "html": True})
            md.enable(["table", "fence"])
            analysis_html = md.render(analysis_text)

            now = datetime.now()
            # Upsert: one analysis per company
            existing = db.query(AIAnalysis).filter(AIAnalysis.company_id == company_id).first()
            if existing:
                existing.analysis_text = analysis_text
                existing.analysis_html = analysis_html
                existing.status = AnalysisStatus.COMPLETED
                existing.updated_at = now
            else:
                existing = AIAnalysis(
                    company_id=company_id,
                    analysis_text=analysis_text,
                    analysis_html=analysis_html,
                    status=AnalysisStatus.COMPLETED,
                    created_at=now,
                    updated_at=now,
                )
                db.add(existing)
            db.commit()

            return analysis_text

        except Exception:
            logger.exception("AI analysis failed for company_id=%s", company_id)
            try:
                existing = db.query(AIAnalysis).filter(AIAnalysis.company_id == company_id).first()
                if existing:
                    existing.status = AnalysisStatus.PENDING
                    existing.updated_at = datetime.now()
                    db.commit()
            except Exception:
                logger.exception("Failed to reset analysis status for company_id=%s", company_id)
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

        except Exception:
            logger.exception("AI comparison failed for companies=%s year=%s quarter=%s", company_ids, year, quarter)
            return ""
        finally:
            db.close()
