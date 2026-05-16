from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    family_id = Column(Integer, ForeignKey("families.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # income, expense, investment
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    color = Column(String(7), default="#808080", nullable=False)  # hex color
    icon = Column(String(50), nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    family = relationship("Family", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
