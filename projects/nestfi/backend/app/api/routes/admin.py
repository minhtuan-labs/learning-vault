from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.schemas.family import FamilyCreate
from app.models import User, Family, FamilyMember, Category, Invitation
from app.utils.exceptions import ForbiddenException
from datetime import datetime, timedelta
import uuid

router = APIRouter()

DEFAULT_INCOME_CATEGORIES = [
    {"name": "Salary", "color": "#4CAF50", "icon": "dollar-sign"},
    {"name": "Bonus", "color": "#66BB6A", "icon": "gift"},
    {"name": "Freelance", "color": "#81C784", "icon": "briefcase"},
    {"name": "Interest", "color": "#A5D6A7", "icon": "trending-up"},
    {"name": "Other Income", "color": "#C8E6C9", "icon": "plus"},
]

DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "Groceries", "color": "#FF9800", "icon": "shopping-cart"},
    {"name": "Utilities", "color": "#FB8C00", "icon": "zap"},
    {"name": "Entertainment", "color": "#F57C00", "icon": "film"},
    {"name": "Transport", "color": "#E65100", "icon": "navigation"},
    {"name": "Cash Withdrawal", "color": "#BF360C", "icon": "credit-card"},
    {"name": "Other Expense", "color": "#FFCCBC", "icon": "minus"},
]

DEFAULT_INVESTMENT_CATEGORIES = [
    {"name": "Stock Portfolio", "color": "#2196F3", "icon": "bar-chart-2"},
    {"name": "Retirement", "color": "#1976D2", "icon": "shield"},
    {"name": "Crypto", "color": "#1565C0", "icon": "hash"},
    {"name": "Other Investment", "color": "#0D47A1", "icon": "trending-up"},
]

@router.post("/families", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_family_admin(
    payload: FamilyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "superadmin":
        raise ForbiddenException("Only superadmin can create families")

    family = Family(
        name=payload.name,
        description=payload.description,
        currency=payload.currency,
        created_by_user_id=current_user.id
    )
    db.add(family)
    db.flush()

    # Add owner if provided
    if payload.owner_email:
        owner = db.query(User).filter(User.email == payload.owner_email).first()
        if owner:
            member = FamilyMember(
                family_id=family.id,
                user_id=owner.id,
                role="owner",
                status="active",
                joined_at=datetime.utcnow()
            )
            db.add(member)

    # Create default categories
    for cat in DEFAULT_INCOME_CATEGORIES:
        db.add(Category(
            family_id=family.id,
            type="income",
            name=cat["name"],
            color=cat["color"],
            icon=cat["icon"],
            is_default=True,
            is_active=True
        ))

    for cat in DEFAULT_EXPENSE_CATEGORIES:
        db.add(Category(
            family_id=family.id,
            type="expense",
            name=cat["name"],
            color=cat["color"],
            icon=cat["icon"],
            is_default=True,
            is_active=True
        ))

    for cat in DEFAULT_INVESTMENT_CATEGORIES:
        db.add(Category(
            family_id=family.id,
            type="investment",
            name=cat["name"],
            color=cat["color"],
            icon=cat["icon"],
            is_default=True,
            is_active=True
        ))

    db.commit()

    return {
        "id": family.id,
        "name": family.name,
        "description": family.description,
        "currency": family.currency,
        "created_at": family.created_at
    }
