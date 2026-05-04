from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models.company import ExchangeEnum
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyResponse])
def list_companies(
    search: str | None = None,
    exchange: ExchangeEnum | None = None,
    industry: str | None = None,
    db: Session = Depends(get_db_session),
):
    service = CompanyService(db)
    return service.list_companies(search=search, exchange=exchange, industry=industry)


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db_session)):
    service = CompanyService(db)
    return service.create_company(payload)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db_session)):
    service = CompanyService(db)
    return service.get_company(company_id)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db_session)):
    service = CompanyService(db)
    return service.update_company(company_id, payload)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db_session)):
    service = CompanyService(db)
    service.delete_company(company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
