from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.ai_analysis import AnalysisStatus


class AIAnalysisResponse(BaseModel):
    id: int
    company_id: int
    period_id: int
    period_label: str
    analysis_text: str
    analysis_html: str
    status: str = "PENDING"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
