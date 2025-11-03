from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class WatchlistBase(BaseModel):
	ticker: str
	buy_price: float
	notify_enabled: bool = False


class WatchlistCreate(WatchlistBase):
	pass


class WatchlistUpdate(BaseModel):
	buy_price: Optional[float] = None
	notify_enabled: Optional[bool] = None


class Watchlist(WatchlistBase):
	id: int
	owner_id: int
	created_at: datetime
	updated_at: datetime
	model_config = ConfigDict(from_attributes=True)

