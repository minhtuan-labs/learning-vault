from sqlalchemy import Column, String, DateTime, func, ForeignKey, BigInteger, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.database import Base


class AccountTypeEnum(str, enum.Enum):
    bank = "bank"
    savings = "savings"
    investment = "investment"
    credit = "credit"
    cash = "cash"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(AccountTypeEnum), nullable=False)
    balance_cents = Column(BigInteger, default=0, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
