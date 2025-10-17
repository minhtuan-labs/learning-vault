from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from models.fund_trade import FundTradeTypeEnum


class FundTradeBase(BaseModel):
	trade_type: FundTradeTypeEnum
	trade_date: datetime
	quantity: float
	price: float
	fee: float = 0.0
	notes: Optional[str] = None


class FundTradeCreate(FundTradeBase):
	pass


class FundTradeUpdate(BaseModel):
	trade_date: Optional[datetime] = None
	quantity: Optional[float] = None
	price: Optional[float] = None
	fee: Optional[float] = None
	notes: Optional[str] = None


class FundTrade(FundTradeBase):
	id: int
	portfolio_id: int
	model_config = ConfigDict(from_attributes=True)

