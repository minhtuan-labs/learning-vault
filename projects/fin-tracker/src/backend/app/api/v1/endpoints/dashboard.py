from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.dashboard import DashboardOverview
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(db: Session = Depends(get_db_session)):
    svc = DashboardService(db)
    return svc.get_overview()
