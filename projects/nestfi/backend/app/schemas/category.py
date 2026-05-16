from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CategoryCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    color: str = "#808080"
    icon: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    family_id: int
    name: str
    type: str
    description: Optional[str]
    color: str
    icon: Optional[str]
    is_default: bool
    is_active: bool
    transaction_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
