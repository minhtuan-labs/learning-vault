from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

# Import Enum từ model để tái sử dụng
from models.stock_trade import StockTradeTypeEnum

# --- Schemas cho StockTrade ---

class StockTradeBase(BaseModel):
	trade_type: StockTradeTypeEnum
	trade_date: datetime
	quantity: float
	price: float
	fee: float = 0.0
	notes: Optional[str] = None

class StockTradeCreate(StockTradeBase):
	pass # portfolio_id sẽ được cung cấp trong logic của API

class StockTradeUpdate(BaseModel):
	trade_date: Optional[datetime] = None
	quantity: Optional[float] = None
	price: Optional[float] = None
	fee: Optional[float] = None
	notes: Optional[str] = None

class StockTrade(StockTradeBase):
	id: int
	portfolio_id: int
	model_config = ConfigDict(from_attributes=True)


# --- Schemas cho StockPortfolio ---

class StockPortfolioBase(BaseModel):
	ticker: str
	target_price: Optional[float] = None
	stop_loss_price: Optional[float] = None
	notes: Optional[str] = None

class StockPortfolioCreate(StockPortfolioBase):
	pass # asset_id sẽ được cung cấp trong logic của API

class StockPortfolioUpdate(BaseModel):
	target_price: Optional[float] = None
	stop_loss_price: Optional[float] = None
	notes: Optional[str] = None

# Schema này dùng để trả về, bao gồm cả lịch sử giao dịch lồng bên trong
class StockPortfolio(StockPortfolioBase):
	id: int
	asset_id: int
	trades: List[StockTrade] = []
	model_config = ConfigDict(from_attributes=True)

