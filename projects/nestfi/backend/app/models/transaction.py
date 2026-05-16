from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Date, Numeric
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    family_id = Column(Integer, ForeignKey("families.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # income, expense, cash_withdrawal
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(1000), nullable=True)
    transaction_date = Column(Date, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True, index=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    family = relationship("Family", back_populates="transactions")
    user = relationship("User", back_populates="transactions", foreign_keys=[user_id])
    category = relationship("Category", back_populates="transactions")
