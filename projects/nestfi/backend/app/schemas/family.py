from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class FamilySchema(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class FamilyListResponse(BaseModel):
    families: list[FamilySchema]
