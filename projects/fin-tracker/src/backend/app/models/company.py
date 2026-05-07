import enum

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ExchangeEnum(str, enum.Enum):
    HOSE = "HOSE"
    HNX = "HNX"
    UPCOM = "UPCOM"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    exchange: Mapped[ExchangeEnum] = mapped_column(
        Enum(ExchangeEnum, name="exchange_enum"), nullable=False, index=True
    )
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    periods = relationship("FinancialPeriod", back_populates="company", cascade="all, delete-orphan")
    summaries = relationship("CompanySummary", back_populates="company", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="company", cascade="all, delete-orphan", lazy="selectin")
    alerts = relationship("Alert", back_populates="company", cascade="all, delete-orphan")
