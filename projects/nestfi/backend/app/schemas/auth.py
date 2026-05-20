from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserSchema(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class MeResponse(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    is_superadmin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
