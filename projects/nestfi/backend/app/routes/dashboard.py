from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from uuid import UUID
from datetime import date

from app.database import get_db
from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction, DirectionEnum
from app.models.family import Family, FamilyMembership
from app.dependencies import get_current_user

router = APIRouter(prefix="/families", tags=["dashboard"])


def _compute_balance(account: Account, db: Session) -> int:
    has_txns = db.query(Transaction).filter(
        Transaction.account_id == account.id,
        Transaction.is_enabled == True,
    ).first()
    if not has_txns:
        return account.balance_cents

    income = db.query(sql_func.coalesce(sql_func.sum(Transaction.amount_cents), 0)).filter(
        Transaction.account_id == account.id,
        Transaction.is_enabled == True,
        Transaction.direction == DirectionEnum.in_,
    ).scalar()
    expense = db.query(sql_func.coalesce(sql_func.sum(Transaction.amount_cents), 0)).filter(
        Transaction.account_id == account.id,
        Transaction.is_enabled == True,
        Transaction.direction == DirectionEnum.out,
    ).scalar()
    return account.balance_cents + income - expense


@router.get("/{family_id}/dashboard")
async def family_dashboard(
    family_id: UUID,
    period: str = Query("month", regex="^(month|year)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family_obj = db.query(Family).filter(Family.id == family_id).first()
    if family_obj and not family_obj.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Family is disabled")
    membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id,
    ).first()
    if not membership and not current_user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

    today = date.today()
    if period == "month":
        date_prefix = today.strftime("%Y-%m")
    else:
        date_prefix = today.strftime("%Y")

    account_ids = [
        a.id
        for a in db.query(Account).filter(Account.family_id == family_id).all()
    ]

    if account_ids:
        period_txns = db.query(Transaction).filter(
            Transaction.account_id.in_(account_ids),
            Transaction.is_enabled == True,
            Transaction.date.like(f"{date_prefix}%"),
        ).all()
    else:
        period_txns = []

    total_income_cents = sum(t.amount_cents for t in period_txns if t.direction == DirectionEnum.in_)
    total_expense_cents = sum(t.amount_cents for t in period_txns if t.direction == DirectionEnum.out)
    net_savings_cents = total_income_cents - total_expense_cents

    accounts_data = []
    for a in db.query(Account).filter(Account.family_id == family_id).all():
        accounts_data.append({
            "id": str(a.id),
            "name": a.name,
            "type": a.type.value,
            "balance_cents": _compute_balance(a, db),
            "currency": a.currency,
        })

    if account_ids:
        recent = (
            db.query(Transaction)
            .filter(
                Transaction.account_id.in_(account_ids),
                Transaction.is_enabled == True,
            )
            .order_by(Transaction.date.desc(), Transaction.created_at.desc())
            .limit(5)
            .all()
        )
    else:
        recent = []

    recent_transactions = []
    for t in recent:
        cat = db.query(Category).filter(Category.id == t.category_id).first()
        acct = db.query(Account).filter(Account.id == t.account_id).first()
        recent_transactions.append({
            "id": str(t.id),
            "date": t.date,
            "description": t.description,
            "amount_cents": t.amount_cents,
            "direction": t.direction.value,
            "category_name": cat.name if cat else None,
            "account_name": acct.name if acct else None,
        })

    return {
        "period": period,
        "total_income_cents": total_income_cents,
        "total_expense_cents": total_expense_cents,
        "net_savings_cents": net_savings_cents,
        "accounts": accounts_data,
        "recent_transactions": recent_transactions,
    }
