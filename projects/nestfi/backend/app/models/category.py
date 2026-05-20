from sqlalchemy import Column, String, DateTime, func, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.database import Base


class CategoryTypeEnum(str, enum.Enum):
    income = "income"
    expense = "expense"
    investment = "investment"


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(CategoryTypeEnum), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
