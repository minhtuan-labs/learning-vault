from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List

class TransactionCreate(BaseModel):
    category_id: int
    type: str
    amount: float = Field(gt=0)
    description: Optional[str] = None
    transaction_date: date

class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    family_id: int
    user_id: int
    user_name: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    type: str
    amount: float
    description: Optional[str]
    transaction_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    skip: int
    limit: int
