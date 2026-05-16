from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="member", nullable=False)  # superadmin, owner, member
    is_active = Column(Boolean, default=True, nullable=False)

    family_members = relationship("FamilyMember", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    families_created = relationship("Family", back_populates="created_by", foreign_keys="Family.created_by_user_id")
    invitations_sent = relationship("Invitation", back_populates="invited_by_user", foreign_keys="Invitation.invited_by_user_id")
