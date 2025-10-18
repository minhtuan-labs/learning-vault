import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from .base import Base


class TransactionTypeEnum(enum.Enum):
	DEPOSIT = "deposit"
	WITHDRAWAL = "withdrawal"
	STOCK_SELL = "stock_sell"
	STOCK_BUY = "stock_buy"
	FUND_SELL = "fund_sell"
	FUND_BUY = "fund_buy"
	DIVIDEND_INCOME = "dividend_income"
	FEE = "fee"


class Transaction(Base):
	__tablename__ = "transactions"
	id = Column(Integer, primary_key=True, index=True)
	asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
	amount = Column(Float, nullable=False)
	transaction_type = Column(SQLAlchemyEnum(TransactionTypeEnum), nullable=False)
	transaction_date = Column(DateTime, nullable=False)
	description = Column(String, nullable=True)

	asset = relationship("Asset", back_populates="transactions")
