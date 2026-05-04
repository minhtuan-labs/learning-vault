from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.dashboard import AnalyticsPeriodMetric, CompanyAnalytics, CompareCompanyItem, CompareResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/companies/{company_id}", response_model=CompanyAnalytics)
def get_company_analytics(
    company_id: int,
    periods: int | None = Query(None, description="Số kỳ tối đa, None=tất cả"),
    db: Session = Depends(get_db_session),
):
    svc = AnalyticsService(db)
    return svc.get_company_analytics(company_id, max_periods=periods)


@router.get("/compare", response_model=CompareResponse)
def compare_companies(
    ids: str = Query(..., description="Danh sách company_id cách nhau bởi dấu phẩy"),
    year: int = Query(..., ge=2000, le=2100),
    quarter: int | None = Query(None, ge=1, le=4),
    db: Session = Depends(get_db_session),
):
    company_ids = [int(x.strip()) for x in ids.split(",") if x.strip()]
    svc = AnalyticsService(db)
    return svc.compare_companies(company_ids, year, quarter)
