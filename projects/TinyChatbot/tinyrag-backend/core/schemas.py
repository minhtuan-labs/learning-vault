from pydantic import BaseModel

class Query(BaseModel):
    question: str

class UpdateSource(BaseModel):
    title: str
    description: str

