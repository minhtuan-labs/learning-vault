import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum, String
from sqlalchemy.orm import relationship
from .base import Base


class FundTradeTypeEnum(enum.Enum):
	BUY = "buy"
	SELL = "sell"

class FundTrade(Base):
	__tablename__ = "fund_trades"
	id = Column(Integer, primary_key=True, index=True)
	portfolio_id = Column(Integer, ForeignKey("fund_portfolios.id"), nullable=False)
	trade_type = Column(SQLAlchemyEnum(FundTradeTypeEnum), nullable=False)
	trade_date = Column(DateTime, nullable=False)
	quantity = Column(Float, nullable=False)
	price = Column(Float, nullable=False)
	fee = Column(Float, default=0.0)
	notes = Column(String, nullable=True)

	portfolio = relationship("FundPortfolio", back_populates="trades")
