from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.api.dependencies import get_db, get_current_user
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
)
from app.models import User, Family, FamilyMember, Category, Transaction
from app.utils.exceptions import NotFoundException, ForbiddenException, ConflictException

router = APIRouter()

def verify_owner(user_id: int, family_id: int, db: Session):
    member = db.query(FamilyMember).filter(
        and_(FamilyMember.family_id == family_id, FamilyMember.user_id == user_id)
    ).first()
    if not member or member.role != "owner":
        raise ForbiddenException("Only owner can manage categories")

def verify_family_access(user_id: int, family_id: int, db: Session):
    member = db.query(FamilyMember).filter(
        and_(FamilyMember.family_id == family_id, FamilyMember.user_id == user_id)
    ).first()
    if not member:
        raise ForbiddenException("User not a member of this family")

@router.get("/families/{family_id}/categories", response_model=CategoryListResponse)
def list_categories(
    family_id: int,
    type: str = Query(None),
    active_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_family_access(current_user.id, family_id, db)

    query = db.query(Category).filter(Category.family_id == family_id)

    if type:
        query = query.filter(Category.type == type)
    if active_only:
        query = query.filter(Category.is_active == True)

    categories = query.all()

    result = []
    for cat in categories:
        transaction_count = db.query(func.count(Transaction.id)).filter(
            Transaction.category_id == cat.id
        ).scalar()
        result.append({
            "id": cat.id,
            "family_id": cat.family_id,
            "name": cat.name,
            "type": cat.type,
            "description": cat.description,
            "color": cat.color,
            "icon": cat.icon,
            "is_default": cat.is_default,
            "is_active": cat.is_active,
            "transaction_count": transaction_count,
            "created_at": cat.created_at
        })

    return {"categories": result}

@router.post("/families/{family_id}/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    family_id: int,
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_owner(current_user.id, family_id, db)

    existing = db.query(Category).filter(
        and_(
            Category.family_id == family_id,
            Category.name == payload.name,
            Category.type == payload.type
        )
    ).first()
    if existing:
        raise ConflictException("Category name already exists for this family")

    category = Category(
        family_id=family_id,
        type=payload.type,
        name=payload.name,
        description=payload.description,
        color=payload.color,
        icon=payload.icon,
        is_default=False,
        is_active=True
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    return {
        "id": category.id,
        "family_id": category.family_id,
        "name": category.name,
        "type": category.type,
        "description": category.description,
        "color": category.color,
        "icon": category.icon,
        "is_default": category.is_default,
        "is_active": category.is_active,
        "transaction_count": 0,
        "created_at": category.created_at
    }

@router.put("/families/{family_id}/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    family_id: int,
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_owner(current_user.id, family_id, db)

    category = db.query(Category).filter(
        and_(Category.id == category_id, Category.family_id == family_id)
    ).first()
    if not category:
        raise NotFoundException("Category not found")

    if payload.name:
        category.name = payload.name
    if payload.description is not None:
        category.description = payload.description
    if payload.color:
        category.color = payload.color
    if payload.icon is not None:
        category.icon = payload.icon

    db.commit()
    db.refresh(category)

    transaction_count = db.query(func.count(Transaction.id)).filter(
        Transaction.category_id == category.id
    ).scalar()

    return {
        "id": category.id,
        "family_id": category.family_id,
        "name": category.name,
        "type": category.type,
        "description": category.description,
        "color": category.color,
        "icon": category.icon,
        "is_default": category.is_default,
        "is_active": category.is_active,
        "transaction_count": transaction_count,
        "created_at": category.created_at
    }

@router.delete("/families/{family_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    family_id: int,
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_owner(current_user.id, family_id, db)

    category = db.query(Category).filter(
        and_(Category.id == category_id, Category.family_id == family_id)
    ).first()
    if not category:
        raise NotFoundException("Category not found")

    category.is_active = False
    db.commit()
