from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.company import Company, ExchangeEnum
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_companies(
        self, search: str | None = None, exchange: ExchangeEnum | None = None, industry: str | None = None
    ) -> list[Company]:
        query = select(Company)
        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(or_(Company.code.ilike(keyword), Company.name.ilike(keyword)))
        if exchange:
            query = query.where(Company.exchange == exchange)
        if industry:
            query = query.where(Company.industry.ilike(f"%{industry.strip()}%"))

        query = query.order_by(Company.updated_at.desc())
        return list(self.db.scalars(query).all())

    def get_by_id(self, company_id: int) -> Company | None:
        return self.db.get(Company, company_id)

    def get_by_code(self, code: str) -> Company | None:
        stmt = select(Company).where(Company.code == code.upper().strip())
        return self.db.scalar(stmt)

    def create(self, payload: CompanyCreate) -> Company:
        data = payload.model_dump()
        data["code"] = data["code"].upper().strip()
        company = Company(**data)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update(self, company: Company, payload: CompanyUpdate) -> Company:
        data = payload.model_dump(exclude_unset=True)
        if "code" in data and data["code"]:
            data["code"] = data["code"].upper().strip()

        for key, value in data.items():
            setattr(company, key, value)

        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete(self, company: Company) -> None:
        self.db.delete(company)
        self.db.commit()
