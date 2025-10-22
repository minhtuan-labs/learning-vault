from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from models.saving import SavingTypeEnum


class SavingDetailBase(BaseModel):
    saving_type: SavingTypeEnum
    bank_code: Optional[str] = None
    initial_amount: float
    interest_rate_pa: float
    term_months: Optional[int] = None
    start_date: datetime
    expected_maturity_date: Optional[datetime] = None
    is_matured: bool = False


class SavingDetailCreate(SavingDetailBase):
    pass


class SavingDetailUpdate(BaseModel):
    bank_code: Optional[str] = None
    interest_rate_pa: Optional[float] = None
    actual_settlement_date: Optional[datetime] = None
    matured_amount: Optional[float] = None
    is_matured: Optional[bool] = None


class SavingDetail(SavingDetailBase):
    id: int
    asset_id: int
    actual_settlement_date: Optional[datetime] = None
    matured_amount: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

