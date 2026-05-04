from fastapi import APIRouter

from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.companies import router as companies_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.periods import router as periods_router

api_router = APIRouter()
api_router.include_router(companies_router)
api_router.include_router(periods_router)
api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)
