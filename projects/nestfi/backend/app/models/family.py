from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import Base, TimestampMixin

class Family(Base, TimestampMixin):
    __tablename__ = "families"

    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_by = relationship("User", back_populates="families_created", foreign_keys=[created_by_user_id])
    family_members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="family", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="family", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="family", cascade="all, delete-orphan")


class FamilyMember(Base, TimestampMixin):
    __tablename__ = "family_members"

    family_id = Column(Integer, ForeignKey("families.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    role = Column(String(50), default="member", nullable=False)  # owner, member, view_only
    status = Column(String(50), default="active", nullable=False)  # active, pending, declined
    joined_at = Column(DateTime, nullable=True)

    family = relationship("Family", back_populates="family_members")
    user = relationship("User", back_populates="family_members")


class Invitation(Base, TimestampMixin):
    __tablename__ = "invitations"

    email = Column(String(255), nullable=False)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False, index=True)
    token = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    invited_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, accepted, declined
    expires_at = Column(DateTime, nullable=False)

    family = relationship("Family", back_populates="invitations")
    invited_by_user = relationship("User", back_populates="invitations_sent", foreign_keys=[invited_by_user_id])
