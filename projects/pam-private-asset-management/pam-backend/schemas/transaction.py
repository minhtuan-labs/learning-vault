from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from models.transaction import TransactionTypeEnum


class TransactionBase(BaseModel):
	amount: float
	transaction_type: TransactionTypeEnum
	transaction_date: datetime
	description: Optional[str] = None


class TransactionCreate(TransactionBase):
	pass


class TransactionUpdate(BaseModel):
	amount: Optional[float] = None
	transaction_date: Optional[datetime] = None
	description: Optional[str] = None


class Transaction(TransactionBase):
	id: int
	asset_id: int
	model_config = ConfigDict(from_attributes=True)

