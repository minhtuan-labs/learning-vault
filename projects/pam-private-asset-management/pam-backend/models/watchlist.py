from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Watchlist(Base):
	__tablename__ = "watchlists"
	id = Column(Integer, primary_key=True, index=True)
	owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	ticker = Column(String, index=True, nullable=False)
	buy_price = Column(Float, nullable=False)
	notify_enabled = Column(Boolean, default=False, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

	owner = relationship("User", back_populates="watchlists")
	__table_args__ = (UniqueConstraint('owner_id', 'ticker', name='_user_ticker_uc'), )

