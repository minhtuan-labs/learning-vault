from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class AccountSchema(BaseModel):
    id: UUID
    name: str
    type: str
    balance_cents: int
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    accounts: list[AccountSchema]


class AccountCreateRequest(BaseModel):
    name: str
    type: str
    initial_balance_cents: int = 0
    currency: str = "USD"


class AccountUpdateRequest(BaseModel):
    name: str | None = None
    type: str | None = None
