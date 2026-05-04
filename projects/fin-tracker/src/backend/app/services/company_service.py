from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.company import Company, ExchangeEnum
from app.repositories.company_repository import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    def __init__(self, db: Session):
        self.repository = CompanyRepository(db)

    def list_companies(
        self, search: str | None = None, exchange: ExchangeEnum | None = None, industry: str | None = None
    ) -> list[Company]:
        return self.repository.list_companies(search=search, exchange=exchange, industry=industry)

    def get_company(self, company_id: int) -> Company:
        company = self.repository.get_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy doanh nghiệp.",
            )
        return company

    def create_company(self, payload: CompanyCreate) -> Company:
        existing = self.repository.get_by_code(payload.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã chứng khoán đã tồn tại.",
            )
        return self.repository.create(payload)

    def update_company(self, company_id: int, payload: CompanyUpdate) -> Company:
        company = self.get_company(company_id)
        if payload.code and payload.code.strip().upper() != company.code:
            existing = self.repository.get_by_code(payload.code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mã chứng khoán đã tồn tại.",
                )
        return self.repository.update(company, payload)

    def delete_company(self, company_id: int) -> None:
        company = self.get_company(company_id)
        self.repository.delete(company)
