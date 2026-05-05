from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    company_id: int
    company_code: str
    company_name: str
    period_id: int
    period_label: str
    alert_type: str
    severity: str
    description: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MarkReadResponse(BaseModel):
    success: bool
