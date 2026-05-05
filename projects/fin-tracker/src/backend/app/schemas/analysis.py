from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AIAnalysisResponse(BaseModel):
    id: int
    company_id: int
    period_id: int
    period_label: str
    analysis_text: str
    analysis_html: str
    created_at: datetime

    class Config:
        from_attributes = True
