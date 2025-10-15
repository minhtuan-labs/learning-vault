import enum
from datetime import datetime
from sqlalchemy import (
	Column,
	Integer,
	String,
	Float,
	DateTime,
	ForeignKey,
	Enum as SQLAlchemyEnum)
from sqlalchemy.orm import relationship
from .base import Base

class AssetTypeEnum(enum.Enum):
	CASH = "cash"
	STOCKS = "stocks"
	SAVINGS = "savings"
	FUNDS = "funds"

class Asset(Base):
	__tablename__ = "assets"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	asset_type = Column(SQLAlchemyEnum(AssetTypeEnum), nullable=False)
	current_value = Column(Float, default=0.0, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)

	owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

	# Relationships
	owner = relationship("User", back_populates="assets")
	transactions = relationship("Transaction", back_populates="asset", cascade="all, delete-orphan")

	# One-to-one detail relationships
	stock_details = relationship("StockDetail", back_populates="asset", uselist=False, cascade="all, delete-orphan")
	savings_details = relationship("SavingDetail", back_populates="asset", uselist=False, cascade="all, delete-orphan")

class StockDetail(Base):
	__tablename__ = "stock_details"

	id = Column(Integer, primary_key=True, index=True)
	asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)
	ticker = Column(String, index=True, nullable=False)
	target_price = Column(Float, nullable=True)
	stop_loss_price = Column(Float, nullable=True)

	asset = relationship("Asset", back_populates="stock_details")

class SavingDetail(Base):
	__tablename__ = "saving_details"

	id = Column(Integer, primary_key=True, index=True)
	asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)
	initial_amount = Column(Float, nullable=False)
	interest_rate = Column(Float, nullable=False)
	start_date = Column(DateTime, nullable=False)
	end_date = Column(DateTime, nullable=False)

	asset = relationship("Asset", back_populates="savings_details")
