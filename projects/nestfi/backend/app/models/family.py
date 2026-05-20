from sqlalchemy import Column, String, DateTime, func, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.database import Base


class RoleEnum(str, enum.Enum):
    owner = "owner"
    member = "member"


class StatusEnum(str, enum.Enum):
    active = "active"
    pending = "pending"
    disabled = "disabled"


class Family(Base):
    __tablename__ = "families"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, server_default='true')
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class FamilyMembership(Base):
    __tablename__ = "family_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.member, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.active, nullable=False)
    joined_at = Column(DateTime, server_default=func.now(), nullable=False)
