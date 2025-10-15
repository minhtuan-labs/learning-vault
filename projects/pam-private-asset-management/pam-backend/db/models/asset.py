import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from .base import Base


class AssetTypeEnum(enum.Enum):
	CASH = "cash"
	STOCKS = "stocks"
	FUNDS = "funds"
	SAVINGS = "savings"


class Asset(Base):
	__tablename__ = "assets"
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	asset_type = Column(SQLAlchemyEnum(AssetTypeEnum), nullable=False)
	cost_basis = Column(Float, default=0.0, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

	owner = relationship("User", back_populates="assets")
	transactions = relationship("Transaction", back_populates="asset", cascade="all, delete-orphan")
	stock_portfolios = relationship("StockPortfolio", back_populates="asset", cascade="all, delete-orphan")
	fund_portfolios = relationship("FundPortfolio", back_populates="asset", cascade="all, delete-orphan")
	savings_details = relationship("SavingDetail", back_populates="asset", uselist=False, cascade="all, delete-orphan")

