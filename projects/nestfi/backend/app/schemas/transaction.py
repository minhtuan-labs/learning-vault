from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class TransactionSchema(BaseModel):
    id: UUID
    account_id: UUID
    category_id: UUID
    category_name: str | None = None
    account_name: str | None = None
    amount_cents: int
    direction: str
    date: str
    description: str | None
    creator_id: UUID
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    transactions: list[TransactionSchema]
    total_count: int
    has_more: bool


class TransactionCreateRequest(BaseModel):
    category_id: UUID
    amount_cents: int
    direction: str
    date: str
    description: str | None = None


class TransactionUpdateRequest(BaseModel):
    amount_cents: int | None = None
    direction: str | None = None
    date: str | None = None
    description: str | None = None
    category_id: UUID | None = None


class TransactionToggleRequest(BaseModel):
    is_enabled: bool
