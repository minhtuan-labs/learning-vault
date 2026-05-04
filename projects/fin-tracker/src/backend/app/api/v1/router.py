from fastapi import APIRouter

from app.api.v1.endpoints.companies import router as companies_router

api_router = APIRouter()
api_router.include_router(companies_router)
