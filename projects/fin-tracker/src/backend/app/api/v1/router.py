from fastapi import APIRouter

from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.companies import router as companies_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.periods import router as periods_router
from app.api.v1.endpoints.alerts import router as alerts_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.settings import router as settings_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(companies_router)
api_router.include_router(periods_router)
api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)
api_router.include_router(alerts_router)
api_router.include_router(analysis_router)
api_router.include_router(settings_router)
