from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from app.api.dependencies import get_db, get_current_user
from app.schemas.analytics import SummaryResponse, TrendsResponse, CategoryBreakdown, TrendData
from app.models import User, FamilyMember, Transaction, Category
from app.utils.exceptions import ForbiddenException, NotFoundException
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

router = APIRouter()

def verify_family_access(user_id: int, family_id: int, db: Session):
    member = db.query(FamilyMember).filter(
        and_(FamilyMember.family_id == family_id, FamilyMember.user_id == user_id)
    ).first()
    if not member:
        raise ForbiddenException("User not a member of this family")

@router.get("/families/{family_id}/analytics/summary", response_model=SummaryResponse)
def get_summary(
    family_id: int,
    period: str = Query("month"),  # month or year
    reference_date: date = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_family_access(current_user.id, family_id, db)

    if not reference_date:
        reference_date = date.today()

    if period == "year":
        period_start = date(reference_date.year, 1, 1)
        period_end = date(reference_date.year, 12, 31)
    else:  # month
        period_start = date(reference_date.year, reference_date.month, 1)
        if reference_date.month == 12:
            period_end = date(reference_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            period_end = date(reference_date.year, reference_date.month + 1, 1) - timedelta(days=1)

    # Get transactions
    transactions = db.query(Transaction).filter(
        and_(
            Transaction.family_id == family_id,
            Transaction.transaction_date >= period_start,
            Transaction.transaction_date <= period_end,
            Transaction.deleted_at == None
        )
    ).all()

    total_income = 0.0
    total_expense = 0.0
    category_breakdown = {}

    for txn in transactions:
        amount = float(txn.amount)
        if txn.type == "income":
            total_income += amount
        else:
            total_expense += amount

        cat_key = (txn.category_id, txn.category.name if txn.category else "Unknown", txn.type)
        if cat_key not in category_breakdown:
            category_breakdown[cat_key] = {"amount": 0.0, "count": 0}
        category_breakdown[cat_key]["amount"] += amount
        category_breakdown[cat_key]["count"] += 1

    net_savings = total_income - total_expense
    savings_rate = (net_savings / total_income) if total_income > 0 else 0.0

    breakdown_list = []
    for (cat_id, cat_name, cat_type), data in category_breakdown.items():
        percentage = (data["amount"] / (total_income if cat_type == "income" else total_expense) * 100) if (total_income if cat_type == "income" else total_expense) > 0 else 0
        breakdown_list.append({
            "category_id": cat_id,
            "category_name": cat_name,
            "type": cat_type,
            "amount": data["amount"],
            "percentage": round(percentage, 1),
            "transaction_count": data["count"]
        })

    return {
        "family_id": family_id,
        "period": period,
        "period_start": period_start,
        "period_end": period_end,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_savings": net_savings,
        "savings_rate": round(savings_rate, 3),
        "transaction_count": len(transactions),
        "category_breakdown": breakdown_list
    }

@router.get("/families/{family_id}/analytics/trends", response_model=TrendsResponse)
def get_trends(
    family_id: int,
    months: int = Query(6, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_family_access(current_user.id, family_id, db)

    trends = []
    current = date.today()

    for i in range(months):
        month_date = current - relativedelta(months=i)
        month_start = date(month_date.year, month_date.month, 1)
        if month_date.month == 12:
            month_end = date(month_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(month_date.year, month_date.month + 1, 1) - timedelta(days=1)

        month_str = month_date.strftime("%Y-%m")

        transactions = db.query(Transaction).filter(
            and_(
                Transaction.family_id == family_id,
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= month_end,
                Transaction.deleted_at == None
            )
        ).all()

        month_income = 0.0
        month_expense = 0.0
        for txn in transactions:
            amount = float(txn.amount)
            if txn.type == "income":
                month_income += amount
            else:
                month_expense += amount

        trends.insert(0, {
            "month": month_str,
            "income": month_income,
            "expense": month_expense,
            "net": month_income - month_expense
        })

    return {
        "family_id": family_id,
        "months": months,
        "trends": trends
    }
