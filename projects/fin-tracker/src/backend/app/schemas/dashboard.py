from pydantic import BaseModel, ConfigDict


class CompanyOverviewItem(BaseModel):
    id: int
    code: str
    name: str
    exchange: str
    revenue: float
    profit: float
    revenue_growth: float | None
    profit_growth: float | None


class DashboardOverview(BaseModel):
    total_companies: int
    companies_with_reports: int
    total_warnings: int
    latest_period_label: str
    top_revenue_companies: list[CompanyOverviewItem]


class AnalyticsPeriodMetric(BaseModel):
    label: str
    year: int
    quarter: int | None
    period_type: str
    revenue: float | None
    profit_after_tax: float | None
    operating_cash_flow: float | None
    total_assets: float | None
    gross_profit_margin: float | None
    roe: float | None
    roa: float | None
    debt_to_assets: float | None


class CompanyAnalytics(BaseModel):
    company_id: int
    company_code: str
    company_name: str
    periods: list[AnalyticsPeriodMetric]


class CompareCompanyItem(BaseModel):
    id: int
    code: str
    name: str
    revenue: float | None
    profit_after_tax: float | None
    operating_cash_flow: float | None
    total_assets: float | None
    gross_profit_margin: float | None
    roe: float | None
    roa: float | None
    debt_to_assets: float | None


class CompareResponse(BaseModel):
    year: int
    quarter: int | None
    period_type: str
    companies: list[CompareCompanyItem]
