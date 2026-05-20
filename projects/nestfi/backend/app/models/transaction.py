from sqlalchemy import Column, String, DateTime, func, ForeignKey, BigInteger, Boolean, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.database import Base


class DirectionEnum(str, enum.Enum):
    in_ = "in"
    out = "out"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    amount_cents = Column(BigInteger, nullable=False)
    direction = Column(Enum(DirectionEnum), nullable=False)
    date = Column(String, nullable=False)  # ISO 8601 date string
    description = Column(String, nullable=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TransactionEdit(Base):
    __tablename__ = "transaction_edits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    editor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    before_snapshot = Column(JSON, nullable=False)
    after_snapshot = Column(JSON, nullable=False)
    edited_at = Column(DateTime, server_default=func.now(), nullable=False)
