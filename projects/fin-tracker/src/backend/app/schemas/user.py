from pydantic import BaseModel


class UserUpdateRequest(BaseModel):
    is_admin: bool | None = None
    is_active: bool | None = None