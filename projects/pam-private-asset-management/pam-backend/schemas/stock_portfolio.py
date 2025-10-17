from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from .stock_trade import StockTrade


    class StockPortfolioBase(BaseModel):
        ticker: str
        target_price: Optional[float] = None
        stop_loss_price: Optional[float] = None
        notes: Optional[str] = None


    class StockPortfolioCreate(StockPortfolioBase):
        pass


    class StockPortfolioUpdate(BaseModel):
        target_price: Optional[float] = None
        stop_loss_price: Optional[float] = None
        notes: Optional[str] = None


    class StockPortfolio(StockPortfolioBase):
        id: int
        asset_id: int
        trades: List[StockTrade] = []
        model_config = ConfigDict(from_attributes=True)

