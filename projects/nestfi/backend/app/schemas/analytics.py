from pydantic import BaseModel
from datetime import date
from typing import List

class CategoryBreakdown(BaseModel):
    category_id: int
    category_name: str
    type: str
    amount: float
    percentage: float
    transaction_count: int

class SummaryResponse(BaseModel):
    family_id: int
    period: str
    period_start: date
    period_end: date
    total_income: float
    total_expense: float
    net_savings: float
    savings_rate: float
    transaction_count: int
    category_breakdown: List[CategoryBreakdown]

class TrendData(BaseModel):
    month: str
    income: float
    expense: float
    net: float

class TrendsResponse(BaseModel):
    family_id: int
    months: int
    trends: List[TrendData]
