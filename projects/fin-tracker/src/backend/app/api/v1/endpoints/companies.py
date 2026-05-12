from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.models.company import ExchangeEnum
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyResponse, CompanySummaryResponse, CompanyUpdate
from app.schemas.financial import FinancialPeriodCreate, FinancialPeriodResponse
from app.services.company_service import CompanyService
from app.services.period_service import PeriodService
from app.services.settings_service import is_enabled
from app.services.summary_service import SummaryService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyResponse])
def list_companies(
    search: str | None = None,
    exchange: ExchangeEnum | None = None,
    industry: str | None = None,
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    service = CompanyService(db)
    return service.list_companies(search=search, exchange=exchange, industry=industry)


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    service = CompanyService(db)
    return service.create_company(payload)


@router.post(
    "/{company_id}/periods",
    response_model=FinancialPeriodResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_financial_period(
    company_id: int,
    payload: FinancialPeriodCreate,
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    svc = PeriodService(db)
    period = svc.create_period(company_id, payload)
    return FinancialPeriodResponse.model_validate(period)


@router.get("/{company_id}/periods", response_model=list[FinancialPeriodResponse])
def list_financial_periods(company_id: int, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    svc = PeriodService(db)
    periods = svc.list_periods(company_id)
    return [FinancialPeriodResponse.model_validate(p) for p in periods]


@router.delete("/{company_id}/periods/{period_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_financial_period(
    company_id: int,
    period_id: int,
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    svc = PeriodService(db)
    svc.delete_period(company_id, period_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    service = CompanyService(db)
    return service.get_company(company_id)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    service = CompanyService(db)
    return service.update_company(company_id, payload)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    service = CompanyService(db)
    service.delete_company(company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{company_id}/summary")
def get_company_summary(company_id: int, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    CompanyService(db).get_company(company_id)
    summary = SummaryService(db).get_summary(company_id)
    if not summary:
        return {"company_id": company_id, "summary_text": None, "generated_at": None}
    return CompanySummaryResponse.model_validate(summary)


@router.post("/{company_id}/summary", response_model=CompanySummaryResponse)
def generate_company_summary(company_id: int, db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    if not is_enabled(db, "ai_summary_enabled"):
        raise HTTPException(status_code=403, detail="Chức năng tóm tắt AI đang tắt. Vui lòng bật lại trong Cài đặt hệ thống.")
    CompanyService(db).get_company(company_id)
    summary = SummaryService(db).generate_and_save(company_id)
    return CompanySummaryResponse.model_validate(summary)