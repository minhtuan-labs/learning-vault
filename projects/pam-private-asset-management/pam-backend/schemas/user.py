from pydantic import BaseModel, Field


# Base schema for User, containing common fields
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


# Schema for creating a new user (includes password)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6) # Password should be hashed before saving


# Schema for updating an existing user (password is optional, as it might not always be updated)
class UserUpdate(UserBase):
    password: str | None = Field(None, min_length=6)
    username: str | None = Field(None, min_length=3, max_length=50) # Allow username to be optional for update


# Schema for returning user data (does not include password hash)
class UserInDBBase(UserBase):
    id: int | None = None # id will be assigned by the database
    is_active: bool = True # A flag to indicate if user is active, default to True

    class Config:
        from_attributes = True # Allows Pydantic to read data from ORM models directly (e.g., SQLAlchemy)


# Specific schema for reading a user from the database
class User(UserInDBBase):
    pass # No additional fields for now, but good practice to keep this separation


# Specific schema for full user details in DB (might include sensitive fields like hashed_password, for internal use)
class UserInDB(UserInDBBase):
    hashed_password: str

