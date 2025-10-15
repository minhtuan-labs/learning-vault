import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from .base import Base


class SavingTypeEnum(enum.Enum):
	TERM_DEPOSIT = "term_deposit"
	CERTIFICATE_OF_DEPOSIT = "certificate_of_deposit"


class SavingDetail(Base):
	__tablename__ = "saving_details"
	id = Column(Integer, primary_key=True, index=True)
	asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)
	saving_type = Column(SQLAlchemyEnum(SavingTypeEnum), nullable=False)
	bank_code = Column(String(10), nullable=True)
	initial_amount = Column(Float, nullable=False)
	interest_rate_pa = Column(Float, nullable=False)
	term_months = Column(Integer, nullable=True)
	start_date = Column(DateTime, nullable=False)
	expected_maturity_date = Column(DateTime, nullable=True)
	actual_settlement_date = Column(DateTime, nullable=True)
	matured_amount = Column(Float, nullable=True)

	asset = relationship("Asset", back_populates="savings_details")

