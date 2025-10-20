from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from models.stock_trade import StockTradeTypeEnum


class StockTradeBase(BaseModel):
	trade_type: StockTradeTypeEnum
	trade_date: datetime
	quantity: float
	price: float
	fee: float = 0.0
	notes: Optional[str] = None
	is_hidden: bool = False


class StockTradeCreate(StockTradeBase):
	pass


class StockTradeUpdate(BaseModel):
	trade_date: Optional[datetime] = None
	quantity: Optional[float] = None
	price: Optional[float] = None
	fee: Optional[float] = None
	notes: Optional[str] = None
	is_hidden: Optional[bool] = None


class StockTrade(StockTradeBase):
	id: int
	portfolio_id: int
	ticker: str
	created_at: datetime
	model_config = ConfigDict(from_attributes=True)
