import enum
from datetime import datetime
from sqlalchemy import (
	Column,
	Integer,
	String,
	Float,
	DateTime,
	ForeignKey,
	Enum as SQLAlchemyEnum,
)
from sqlalchemy.orm import relationship
from .base import Base

class TransactionTypeEnum(enum.Enum):
	DEPOSIT = "deposit"
	WITHDRAWAL = "withdrawal"
	BUY = "buy"
	SELL = "sell"
	DIVIDEND = "dividend"
	INTEREST = "interest"

class Transaction(Base):
	__tablename__ = "transactions"

	id = Column(Integer, primary_key=True, index=True)
	asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

	amount = Column(Float, nullable=False)
	transaction_type = Column(SQLAlchemyEnum(TransactionTypeEnum), nullable=False)
	transaction_date = Column(DateTime, default=datetime.utcnow)
	description = Column(String, nullable=True)

	# Optional fields, mainly for stock transactions
	quantity = Column(Float, nullable=True)
	price_per_unit = Column(Float, nullable=True)

	asset = relationship("Asset", back_populates="transactions")
