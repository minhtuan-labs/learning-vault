from __future__ import annotations

import enum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.company import Company


class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True)
    analysis_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    analysis_html: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[AnalysisStatus] = mapped_column(Enum(AnalysisStatus, name="analysis_status"), nullable=False, default=AnalysisStatus.PENDING)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    company = relationship("Company", back_populates="ai_analyses")
