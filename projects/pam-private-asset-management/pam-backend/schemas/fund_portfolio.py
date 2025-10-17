from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from .fund_trade import FundTrade


class FundPortfolioBase(BaseModel):
	ticker: str
	notes: Optional[str] = None


class FundPortfolioCreate(FundPortfolioBase):
	pass

class FundPortfolioUpdate(BaseModel):
	notes: Optional[str] = None


class FundPortfolio(FundPortfolioBase):
	id: int
	asset_id: int
	trades: List[FundTrade] = []
	model_config = ConfigDict(from_attributes=True)

