from pydantic import BaseModel
from typing import Optional

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 30

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
