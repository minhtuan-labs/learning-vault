from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.financial import PeriodTypeEnum, ReportTypeEnum


class FinancialPeriodCreate(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    quarter: int | None = Field(None, ge=1, le=4)
    period_type: PeriodTypeEnum


class FinancialPeriodResponse(BaseModel):
    id: int
    company_id: int
    year: int
    quarter: int | None
    period_type: PeriodTypeEnum
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ReportFileResponse(BaseModel):
    id: int
    period_id: int
    report_type: ReportTypeEnum
    file_name: str
    file_path: str
    file_size: int
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FinancialDataResponse(BaseModel):
    id: int
    period_id: int
    report_type: ReportTypeEnum
    metric_name: str
    metric_value: float
    unit: str
    is_verified: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_validator("metric_value", mode="before")
    @classmethod
    def metric_value_to_float(cls, v):
        if isinstance(v, Decimal):
            return float(v)
        return v


class FinancialDataUpdate(BaseModel):
    metric_value: float
    unit: str | None = None


class ExtractRequest(BaseModel):
    file_id: int | None = None
