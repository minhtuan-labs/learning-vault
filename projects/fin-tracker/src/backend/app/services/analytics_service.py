from __future__ import annotations

from sqlalchemy import nulls_last, select, desc
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.financial import (
    FinancialData,
    FinancialPeriod,
    ReportFile,
    ReportTypeEnum,
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
_CDKT_ASSET_KEYS = ["Tổng tài sản", "TỔNG TÀI SẢN"]
_CDKT_EQUITY_KEYS = ["Vốn chủ sở hữu", "Nguồn vốn chủ sở hữu"]
_CDKT_DEBT_KEYS = ["Nợ phải trả", "NỢ PHẢI TRẢ"]
_LCTT_OCF_KEYS = [
    "Lưu chuyển tiền thuần từ hoạt động kinh doanh",
    "Lưu chuyển tiền thuần từ HĐKD",
    "Tiền thuần từ HĐKD",
]
_KQKD_GROSS_PROFIT_KEYS = ["Lợi nhuận gộp", "Lợi nhuận gộp từ bán hàng và cung cấp dịch vụ"]
_BANK_LOAN_KEYS = ["Cho vay khách hàng", "Dư nợ cho vay khách hàng", "Tổng dư nợ cho vay"]
_BANK_DEPOSIT_KEYS = ["Tiền gửi khách hàng", "Tiền gửi của khách hàng"]
_BANK_NPL_KEYS = ["Nợ xấu", "Tỷ lệ nợ xấu", "NPL"]
_BANK_CAR_KEYS = ["CAR", "Hệ số CAR", "Tỷ lệ an toàn vốn"]
_BANK_NIM_KEYS = ["NIM", "Tỷ lệ thu nhập lãi thuần"]
_BANK_LDR_KEYS = ["LDR", "Tỷ lệ cho vay trên tiền gửi"]
_BANK_CASA_KEYS = ["CASA", "Tỷ lệ CASA"]

_BANK_KEYWORDS = ["Ngân hàng", "ngân hàng", "Banking", "banking", "Tài chính", "tài chính", "Finance", "finance", "Credit", "credit", "Tín dụng", "tín dụng"]


def _match(metrics: dict[str, float], keys: list[str]) -> float | None:
    for key in keys:
        for m_name, m_val in metrics.items():
            if key.lower() in m_name.lower():
                return m_val
    return None


def _is_bank(industry: str | None) -> bool:
    if not industry:
        return False
    return any(kw in industry for kw in _BANK_KEYWORDS)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_company_analytics(self, company_id: int, max_periods: int | None = None) -> dict:
        company = self.db.get(Company, company_id)
        if not company:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy doanh nghiệp.")

        is_bank_entity = _is_bank(company.industry)
        revenue_keys = _BANK_REVENUE_KEYS if is_bank_entity else _KQKD_REVENUE_KEYS
        profit_keys = _BANK_PROFIT_KEYS

        stmt = (
            select(FinancialPeriod)
            .where(FinancialPeriod.company_id == company_id)
            .join(ReportFile, ReportFile.period_id == FinancialPeriod.id)
            .order_by(FinancialPeriod.year.desc(), nulls_last(desc(FinancialPeriod.quarter)))
        )
        if max_periods:
            stmt = stmt.limit(max_periods)

        periods = list(self.db.scalars(stmt).all())

        periods_out = []
        for p in periods:
            data_rows = self.db.execute(
                select(FinancialData.metric_name, FinancialData.metric_value, FinancialData.report_type)
                .where(FinancialData.period_id == p.id)
            ).all()
            metrics = {dr.metric_name: float(dr.metric_value) for dr in data_rows}

            revenue = _match(metrics, revenue_keys)
            profit = _match(metrics, profit_keys)
            ocf = _match(metrics, _LCTT_OCF_KEYS)
            total_assets = _match(metrics, _CDKT_ASSET_KEYS)
            gross_profit = _match(metrics, _KQKD_GROSS_PROFIT_KEYS)
            equity = _match(metrics, _CDKT_EQUITY_KEYS)
            debt = _match(metrics, _CDKT_DEBT_KEYS)

            gross_profit_margin = None
            if gross_profit is not None and revenue is not None and revenue > 0:
                gross_profit_margin = round(gross_profit / revenue * 100, 2)

            roe = None
            if profit is not None and equity is not None and equity > 0:
                roe = round(profit / equity * 100, 2)

            roa = None
            if profit is not None and total_assets is not None and total_assets > 0:
                roa = round(profit / total_assets * 100, 2)

            debt_to_assets = None
            if debt is not None and total_assets is not None and total_assets > 0:
                debt_to_assets = round(debt / total_assets * 100, 2)

            period_data = {
                "label": label if (label := (f"Năm {p.year}" if p.period_type.value == "Y" else f"Quý {p.quarter}/{p.year}")) else "",
                "year": p.year,
                "quarter": p.quarter,
                "period_type": p.period_type.value,
                "revenue": round(revenue / 1_000_000, 2) if revenue is not None else None,
                "profit_after_tax": round(profit / 1_000_000, 2) if profit is not None else None,
                "operating_cash_flow": round(ocf / 1_000_000, 2) if ocf is not None else None,
                "total_assets": round(total_assets / 1_000_000, 2) if total_assets is not None else None,
                "gross_profit_margin": gross_profit_margin,
                "roe": roe,
                "roa": roa,
                "debt_to_assets": debt_to_assets,
            }

            if is_bank_entity:
                loans = _match(metrics, _BANK_LOAN_KEYS)
                deposits = _match(metrics, _BANK_DEPOSIT_KEYS)
                npl = _match(metrics, _BANK_NPL_KEYS)
                nim = _match(metrics, _BANK_NIM_KEYS)
                ldr = _match(metrics, _BANK_LDR_KEYS)
                casa = _match(metrics, _BANK_CASA_KEYS)
                car = _match(metrics, _BANK_CAR_KEYS)

                period_data["loans"] = round(loans / 1_000_000, 2) if loans is not None else None
                period_data["deposits"] = round(deposits / 1_000_000, 2) if deposits is not None else None
                period_data["npl_ratio"] = npl if npl is not None else None
                period_data["nim"] = nim if nim is not None else None
                period_data["ldr"] = ldr if ldr is not None else None
                period_data["casa_ratio"] = casa if casa is not None else None
                period_data["car"] = car if car is not None else None

                if loans is not None and deposits is not None and deposits > 0:
                    period_data["ldr"] = round(loans / deposits * 100, 2)

            periods_out.append(period_data)

        periods_out.sort(key=lambda x: (x["year"], x["quarter"] or 0))

        return {
            "company_id": company.id,
            "company_code": company.code,
            "company_name": company.name,
            "entity_type": "bank" if is_bank_entity else "company",
            "periods": periods_out,
        }

    def compare_companies(self, company_ids: list[int], year: int, quarter: int | None = None) -> dict:
        period_type = "Q" if quarter is not None else "Y"
        companies_out = []

        for cid in company_ids:
            company = self.db.get(Company, cid)
            if not company:
                continue

            is_bank_entity = _is_bank(company.industry)
            revenue_keys = _BANK_REVENUE_KEYS if is_bank_entity else _KQKD_REVENUE_KEYS
            profit_keys = _BANK_PROFIT_KEYS

            stmt = (
                select(FinancialPeriod.id)
                .where(
                    FinancialPeriod.company_id == cid,
                    FinancialPeriod.year == year,
                    FinancialPeriod.quarter == quarter if quarter is not None else FinancialPeriod.quarter.is_(None),
                )
                .join(ReportFile, ReportFile.period_id == FinancialPeriod.id)
                .limit(1)
            )
            period_id = self.db.scalar(stmt)
            if not period_id:
                companies_out.append({
                    "id": cid,
                    "code": company.code,
                    "name": company.name,
                    "entity_type": "bank" if is_bank_entity else "company",
                    "revenue": None,
                    "profit_after_tax": None,
                    "operating_cash_flow": None,
                    "total_assets": None,
                    "gross_profit_margin": None,
                    "roe": None,
                    "roa": None,
                    "debt_to_assets": None,
                })
                continue

            data_rows = self.db.execute(
                select(FinancialData.metric_name, FinancialData.metric_value)
                .where(FinancialData.period_id == period_id)
            ).all()
            metrics = {dr.metric_name: float(dr.metric_value) for dr in data_rows}

            revenue = _match(metrics, revenue_keys)
            profit = _match(metrics, profit_keys)
            ocf = _match(metrics, _LCTT_OCF_KEYS)
            total_assets = _match(metrics, _CDKT_ASSET_KEYS)
            gross_profit = _match(metrics, _KQKD_GROSS_PROFIT_KEYS)
            equity = _match(metrics, _CDKT_EQUITY_KEYS)
            debt = _match(metrics, _CDKT_DEBT_KEYS)

            gross_profit_margin = None
            if gross_profit is not None and revenue is not None and revenue > 0:
                gross_profit_margin = round(gross_profit / revenue * 100, 2)
            roe = None
            if profit is not None and equity is not None and equity > 0:
                roe = round(profit / equity * 100, 2)
            roa = None
            if profit is not None and total_assets is not None and total_assets > 0:
                roa = round(profit / total_assets * 100, 2)
            debt_to_assets = None
            if debt is not None and total_assets is not None and total_assets > 0:
                debt_to_assets = round(debt / total_assets * 100, 2)

            company_out = {
                "id": cid,
                "code": company.code,
                "name": company.name,
                "entity_type": "bank" if is_bank_entity else "company",
                "revenue": round(revenue / 1_000_000, 2) if revenue is not None else None,
                "profit_after_tax": round(profit / 1_000_000, 2) if profit is not None else None,
                "operating_cash_flow": round(ocf / 1_000_000, 2) if ocf is not None else None,
                "total_assets": round(total_assets / 1_000_000, 2) if total_assets is not None else None,
                "gross_profit_margin": gross_profit_margin,
                "roe": roe,
                "roa": roa,
                "debt_to_assets": debt_to_assets,
            }

            if is_bank_entity:
                loans = _match(metrics, _BANK_LOAN_KEYS)
                deposits = _match(metrics, _BANK_DEPOSIT_KEYS)
                npl = _match(metrics, _BANK_NPL_KEYS)
                nim = _match(metrics, _BANK_NIM_KEYS)
                casa = _match(metrics, _BANK_CASA_KEYS)
                car = _match(metrics, _BANK_CAR_KEYS)

                company_out["loans"] = round(loans / 1_000_000, 2) if loans is not None else None
                company_out["deposits"] = round(deposits / 1_000_000, 2) if deposits is not None else None
                company_out["npl_ratio"] = npl if npl is not None else None
                company_out["nim"] = nim if nim is not None else None
                company_out["casa_ratio"] = casa if casa is not None else None
                company_out["car"] = car if car is not None else None

                if loans is not None and deposits is not None and deposits > 0:
                    company_out["ldr"] = round(loans / deposits * 100, 2)
                else:
                    ldr = _match(metrics, _BANK_LDR_KEYS)
                    company_out["ldr"] = ldr if ldr is not None else None

            companies_out.append(company_out)

        return {
            "year": year,
            "quarter": quarter,
            "period_type": period_type,
            "companies": companies_out,
        }
