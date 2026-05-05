from __future__ import annotations

from sqlalchemy import desc, func, nulls_last, select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.financial import (
    FinancialData,
    FinancialPeriod,
    ReportFile,
)

_KQKD_REVENUE_KEYS = ["Doanh thu thuần", "Doanh thu", "Tổng doanh thu"]
_KQKD_PROFIT_KEYS = [
    "Lợi nhuận sau thuế",
    "Lợi nhuận ròng",
    "Lợi nhuận sau thuế TNDN",
    "Lợi nhuận sau thuế thu nhập doanh nghiệp",
]
_BANK_REVENUE_KEYS = [
    "Tổng thu nhập hoạt động",
    "TOI",
    "Tổng thu nhập",
    "Thu nhập hoạt động",
]
_BANK_PROFIT_KEYS = _KQKD_PROFIT_KEYS

_BANK_KEYWORDS = ["Ngân hàng", "ngân hàng", "Banking", "banking", "Tài chính", "tài chính", "Finance", "finance", "Credit", "credit", "Tín dụng", "tín dụng"]

_TO_BILLION = 1_000_000


def _is_bank(industry: str | None) -> bool:
    if not industry:
        return False
    return any(kw in industry for kw in _BANK_KEYWORDS)


def _match(metrics: dict[str, float], keys: list[str]) -> float | None:
    for key in keys:
        for m_name, m_val in metrics.items():
            if key.lower() in m_name.lower():
                return m_val
    return None


def _get_period_metrics(db: Session, period_id: int) -> dict[str, float]:
    rows = db.execute(
        select(FinancialData.metric_name, FinancialData.metric_value)
        .where(FinancialData.period_id == period_id)
    ).all()
    return {dr.metric_name: float(dr.metric_value) for dr in rows}


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> dict:
        total_companies = self.db.scalar(select(func.count(Company.id))) or 0

        stmt_periods = (
            select(
                FinancialPeriod.company_id,
                FinancialPeriod.year,
                FinancialPeriod.quarter,
                FinancialPeriod.period_type,
            )
            .join(ReportFile, ReportFile.period_id == FinancialPeriod.id)
            .where(FinancialPeriod.period_type == "Y")
            .distinct()
        )
        rows = self.db.execute(stmt_periods).all()

        companies_with_reports = len({r.company_id for r in rows})

        latest_year = max((r.year for r in rows), default=0)
        if latest_year > 0:
            latest_label = f"Năm {latest_year}"
        else:
            latest_label = "Chưa có"

        company_latest_period = {}
        for r in rows:
            key = r.company_id
            existing = company_latest_period.get(key)
            if existing is None or r.year > existing:
                company_latest_period[key] = r.year

        company_data = {}
        for company_id in company_latest_period:
            company_obj = self.db.get(Company, company_id)
            is_bank_entity = _is_bank(company_obj.industry if company_obj else None)

            revenue_keys = _BANK_REVENUE_KEYS if is_bank_entity else _KQKD_REVENUE_KEYS
            profit_keys = _BANK_PROFIT_KEYS

            periods_stmt = (
                select(FinancialPeriod.id, FinancialPeriod.year, FinancialPeriod.quarter)
                .where(FinancialPeriod.company_id == company_id)
                .where(FinancialPeriod.period_type == "Y")
                .order_by(FinancialPeriod.year.desc())
            )
            periods = self.db.execute(periods_stmt).all()

            period_metrics_list = []
            for pid, py, pq in periods:
                metrics = _get_period_metrics(self.db, pid)
                period_metrics_list.append({
                    "period_id": pid,
                    "year": py,
                    "quarter": pq,
                    "revenue": _match(metrics, revenue_keys),
                    "profit": _match(metrics, profit_keys),
                })

            period_metrics_list.sort(key=lambda x: x["year"])

            latest_year = company_latest_period[company_id]
            latest_metrics = None
            for pm in period_metrics_list:
                if pm["year"] == latest_year:
                    latest_metrics = pm
                    break

            company_data[company_id] = {
                "latest": latest_metrics,
                "all_periods": period_metrics_list,
            }

        company_list = list(self.db.scalars(select(Company).order_by(Company.name)).all())

        top_revenue = []
        for c in company_list:
            cd = company_data.get(c.id)
            if not cd or not cd["latest"] or cd["latest"]["revenue"] is None:
                continue

            is_bank_entity = _is_bank(c.industry)
            rev = cd["latest"]["revenue"]
            profit = cd["latest"]["profit"]

            all_p = cd["all_periods"]
            latest_idx = None
            for i, pm in enumerate(all_p):
                if pm["period_id"] == cd["latest"]["period_id"]:
                    latest_idx = i
                    break

            revenue_growth = None
            if latest_idx is not None and latest_idx > 0:
                prev_rev = all_p[latest_idx - 1]["revenue"]
                if prev_rev is not None and prev_rev > 0:
                    revenue_growth = (rev - prev_rev) / prev_rev * 100

            profit_growth = None
            if latest_idx is not None and latest_idx > 0 and profit is not None:
                prev_profit = all_p[latest_idx - 1]["profit"]
                if prev_profit is not None and prev_profit != 0:
                    profit_growth = (profit - prev_profit) / abs(prev_profit) * 100

            top_revenue.append({
                "id": c.id,
                "code": c.code,
                "name": c.name,
                "exchange": c.exchange.value if hasattr(c.exchange, "value") else str(c.exchange),
                "industry": c.industry,
                "entity_type": "bank" if is_bank_entity else "company",
                "revenue": round(rev / _TO_BILLION, 2),
                "profit": round(profit / _TO_BILLION, 2) if profit is not None else None,
                "revenue_growth": round(revenue_growth, 2) if revenue_growth is not None else None,
                "profit_growth": round(profit_growth, 2) if profit_growth is not None else None,
            })

        top_revenue.sort(key=lambda x: x["revenue"] or 0, reverse=True)

        return {
            "total_companies": total_companies,
            "companies_with_reports": companies_with_reports,
            "total_warnings": 0,
            "latest_period_label": latest_label,
            "top_revenue_companies": top_revenue[:5],
        }
