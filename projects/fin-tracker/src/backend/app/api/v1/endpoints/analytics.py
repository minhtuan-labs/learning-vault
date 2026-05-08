from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.schemas.dashboard import AnalyticsPeriodMetric, CompanyAnalytics, CompareCompanyItem, CompareResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/companies/{company_id}", response_model=CompanyAnalytics)
def get_company_analytics(
    company_id: int,
    periods: int | None = Query(None, description="Số kỳ tối đa, None=tất cả"),
    period_type: str | None = Query(None, description="Lọc theo loại kỳ: Q=quý, Y=năm"),
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    svc = AnalyticsService(db)
    return svc.get_company_analytics(company_id, max_periods=periods, period_type=period_type)


@router.get("/compare", response_model=CompareResponse)
def compare_companies(
    ids: str = Query(..., description="Danh sách company_id cách nhau bởi dấu phẩy"),
    year: int = Query(..., ge=2000, le=2100),
    quarter: int | None = Query(None, ge=1, le=4),
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    company_ids = [int(x.strip()) for x in ids.split(",") if x.strip()]
    svc = AnalyticsService(db)
    return svc.compare_companies(company_ids, year, quarter)