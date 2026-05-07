import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PeriodTypeEnum(str, enum.Enum):
    Q = "Q"
    Y = "Y"


class ReportTypeEnum(str, enum.Enum):
    KQKD = "KQKD"
    CDKT = "CDKT"
    LCTT = "LCTT"
    TM = "TM"
    CBTT = "CBTT"


class FinancialPeriod(Base):
    __tablename__ = "financial_periods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quarter: Mapped[int | None] = mapped_column(Integer, nullable=True)
    period_type: Mapped[PeriodTypeEnum] = mapped_column(
        Enum(PeriodTypeEnum, name="period_type_enum"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    company: Mapped["Company"] = relationship("Company", back_populates="periods")
    report_files: Mapped[list["ReportFile"]] = relationship(
        "ReportFile", back_populates="period", cascade="all, delete-orphan"
    )
    financial_data_rows: Mapped[list["FinancialData"]] = relationship(
        "FinancialData", back_populates="period", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert", back_populates="period", cascade="all, delete-orphan"
    )


class ReportFile(Base):
    __tablename__ = "report_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("financial_periods.id", ondelete="CASCADE"), index=True)
    report_type: Mapped[ReportTypeEnum] = mapped_column(
        Enum(ReportTypeEnum, name="report_type_enum_files"), nullable=False, index=True
    )
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    period: Mapped["FinancialPeriod"] = relationship("FinancialPeriod", back_populates="report_files")


class FinancialData(Base):
    __tablename__ = "financial_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("financial_periods.id", ondelete="CASCADE"), index=True)
    report_type: Mapped[ReportTypeEnum] = mapped_column(
        Enum(ReportTypeEnum, name="report_type_enum_data"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(512), nullable=False)
    metric_value: Mapped[float] = mapped_column(Numeric(24, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(64), nullable=False, server_default="triệu VND")
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    period: Mapped["FinancialPeriod"] = relationship("FinancialPeriod", back_populates="financial_data_rows")
