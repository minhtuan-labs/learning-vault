import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum, String
from sqlalchemy.orm import relationship
from .base import Base

class StockTradeTypeEnum(enum.Enum):
	BUY = "buy"
	SELL = "sell"
	DIVIDEND_STOCK = "dividend_stock"

class StockTrade(Base):
	__tablename__ = "stock_trades"
	id = Column(Integer, primary_key=True, index=True)
	portfolio_id = Column(Integer, ForeignKey("stock_portfolios.id"), nullable=False)
	trade_type = Column(SQLAlchemyEnum(StockTradeTypeEnum), nullable=False)
	trade_date = Column(DateTime, nullable=False)
	quantity = Column(Float, nullable=False)
	price = Column(Float, nullable=False)
	fee = Column(Float, default=0.0)
	notes = Column(String, nullable=True)

	portfolio = relationship("StockPortfolio", back_populates="trades")
