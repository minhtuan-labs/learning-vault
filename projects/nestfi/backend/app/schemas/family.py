from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class FamilyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner_email: Optional[str] = None
    currency: str = "USD"

class FamilyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class FamilyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    currency: str
    role: Optional[str] = None
    member_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class FamilyDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    currency: str
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FamilyMemberResponse(BaseModel):
    id: int
    user_id: Optional[int]
    email: str
    full_name: Optional[str]
    role: str
    status: str
    joined_at: Optional[datetime]
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FamilyMembersListResponse(BaseModel):
    members: List[FamilyMemberResponse]

class InvitationCreate(BaseModel):
    email: str
    role: str = "member"

class InvitationResponse(BaseModel):
    id: int
    email: str
    role: str
    status: str
    expires_at: datetime
    invitation_sent: bool = True

    class Config:
        from_attributes = True

class InvitationAccept(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None

class InvitationAcceptResponse(BaseModel):
    success: bool
    family_id: int
    family_name: str
    access_token: str
    user: dict
