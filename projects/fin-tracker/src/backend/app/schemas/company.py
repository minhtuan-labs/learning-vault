from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.company import ExchangeEnum


class CompanyBase(BaseModel):
    code: str
    name: str
    exchange: ExchangeEnum
    industry: str | None = None
    description: str | None = None
    website: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    exchange: ExchangeEnum | None = None
    industry: str | None = None
    description: str | None = None
    website: str | None = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
