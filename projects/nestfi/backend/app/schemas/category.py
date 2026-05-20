from pydantic import BaseModel
from uuid import UUID


class CategorySchema(BaseModel):
    id: UUID
    name: str
    type: str
    is_default: bool

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    categories: list[CategorySchema]


class CategoryCreateRequest(BaseModel):
    name: str
    type: str
