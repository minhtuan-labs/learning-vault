from __future__ import annotations

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    period_id: Mapped[int] = mapped_column(Integer, ForeignKey("financial_periods.id", ondelete="CASCADE"), nullable=False)
    analysis_text: Mapped[str] = mapped_column(Text, nullable=False)
    analysis_html: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    company = relationship("Company", back_populates="ai_analyses")
    period = relationship("FinancialPeriod", back_populates="ai_analyses")
