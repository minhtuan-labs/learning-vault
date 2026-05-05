from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.models.alert import Alert
from app.models.company import Company
from app.models.financial import FinancialPeriod
from app.schemas.alert import AlertResponse, MarkReadResponse

router = APIRouter()


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    company_id: int | None = Query(None),
    is_read: bool | None = Query(None),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            Alert.id,
            Alert.company_id,
            Company.code.label("company_code"),
            Company.name.label("company_name"),
            Alert.period_id,
            FinancialPeriod.year,
            FinancialPeriod.quarter,
            Alert.alert_type,
            Alert.severity,
            Alert.description,
            Alert.is_read,
            Alert.created_at,
        )
        .join(Company, Company.id == Alert.company_id)
        .join(FinancialPeriod, FinancialPeriod.id == Alert.period_id)
    )

    if company_id:
        stmt = stmt.where(Alert.company_id == company_id)
    if is_read is not None:
        stmt = stmt.where(Alert.is_read == is_read)

    stmt = stmt.order_by(desc(Alert.created_at)).limit(limit)

    rows = db.execute(stmt).all()

    result = []
    for r in rows:
        period_label = f"Q{r.quarter}/{r.year}" if r.quarter else f"Năm {r.year}"
        result.append(
            AlertResponse(
                id=r.id,
                company_id=r.company_id,
                company_code=r.company_code,
                company_name=r.company_name,
                period_id=r.period_id,
                period_label=period_label,
                alert_type=r.alert_type,
                severity=r.severity,
                description=r.description,
                is_read=r.is_read,
                created_at=r.created_at,
            )
        )
    return result


@router.put("/{alert_id}/read", response_model=MarkReadResponse)
def mark_read(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.is_read = True
    db.commit()
    return MarkReadResponse(success=True)


@router.put("/read-all", response_model=MarkReadResponse)
def mark_all_read(company_id: int | None = Query(None), db: Session = Depends(get_db)):
    stmt = select(Alert).where(Alert.is_read == False)
    if company_id:
        stmt = stmt.where(Alert.company_id == company_id)
    alerts = db.execute(stmt).scalars().all()
    for a in alerts:
        a.is_read = True
    db.commit()
    return MarkReadResponse(success=True)
