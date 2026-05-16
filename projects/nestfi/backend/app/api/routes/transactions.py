from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc
from app.api.dependencies import get_db, get_current_user
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionResponse, TransactionListResponse
)
from app.models import User, Family, FamilyMember, Transaction, Category
from app.utils.exceptions import NotFoundException, ForbiddenException, ValidationException
from datetime import date

router = APIRouter()

def verify_family_access(user_id: int, family_id: int, db: Session):
    member = db.query(FamilyMember).filter(
        and_(FamilyMember.family_id == family_id, FamilyMember.user_id == user_id)
    ).first()
    if not member:
        raise ForbiddenException("User not a member of this family")
    return member.role

@router.get("/families/{family_id}/transactions", response_model=TransactionListResponse)
def list_transactions(
    family_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    category_id: int = Query(None),
    member_id: int = Query(None),
    type: str = Query(None),
    date_from: date = Query(None),
    date_to: date = Query(None),
    sort_by: str = Query("date"),  # date or amount
    sort_order: str = Query("desc"),  # asc or desc
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_family_access(current_user.id, family_id, db)

    # Base query
    query = db.query(Transaction).filter(
        and_(Transaction.family_id == family_id, Transaction.deleted_at == None)
    )

    # Apply filters
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if member_id:
        query = query.filter(Transaction.user_id == member_id)
    if type:
        query = query.filter(Transaction.type == type)
    if date_from:
        query = query.filter(Transaction.transaction_date >= date_from)
    if date_to:
        query = query.filter(Transaction.transaction_date <= date_to)

    # Get total before pagination
    total = query.count()

    # Sort
    if sort_by == "amount":
        order_col = Transaction.amount
    else:
        order_col = Transaction.transaction_date

    if sort_order == "asc":
        query = query.order_by(asc(order_col))
    else:
        query = query.order_by(desc(order_col))

    transactions = query.offset(skip).limit(limit).all()

    result = []
    for txn in transactions:
        result.append({
            "id": txn.id,
            "family_id": txn.family_id,
            "user_id": txn.user_id,
            "user_name": txn.user.full_name if txn.user else None,
            "category_id": txn.category_id,
            "category_name": txn.category.name if txn.category else None,
            "type": txn.type,
            "amount": float(txn.amount),
            "description": txn.description,
            "transaction_date": txn.transaction_date,
            "created_at": txn.created_at,
            "updated_at": txn.updated_at
        })

    return {
        "transactions": result,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/families/{family_id}/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    family_id: int,
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_family_access(current_user.id, family_id, db)

    category = db.query(Category).filter(
        and_(Category.id == payload.category_id, Category.family_id == family_id)
    ).first()
    if not category:
        raise ValidationException("Category not found in this family")

    transaction = Transaction(
        family_id=family_id,
        user_id=current_user.id,
        category_id=payload.category_id,
        type=payload.type,
        amount=payload.amount,
        description=payload.description,
        transaction_date=payload.transaction_date
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {
        "id": transaction.id,
        "family_id": transaction.family_id,
        "user_id": transaction.user_id,
        "user_name": current_user.full_name,
        "category_id": transaction.category_id,
        "category_name": category.name,
        "type": transaction.type,
        "amount": float(transaction.amount),
        "description": transaction.description,
        "transaction_date": transaction.transaction_date,
        "created_at": transaction.created_at,
        "updated_at": transaction.updated_at
    }

@router.put("/families/{family_id}/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    family_id: int,
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_family_access(current_user.id, family_id, db)

    transaction = db.query(Transaction).filter(
        and_(Transaction.id == transaction_id, Transaction.family_id == family_id, Transaction.deleted_at == None)
    ).first()
    if not transaction:
        raise NotFoundException("Transaction not found")

    role = verify_family_access(current_user.id, family_id, db)
    is_author = transaction.user_id == current_user.id
    is_owner = role == "owner"

    if not (is_author or is_owner):
        raise ForbiddenException("Only author or owner can update this transaction")

    if payload.category_id:
        category = db.query(Category).filter(
            and_(Category.id == payload.category_id, Category.family_id == family_id)
        ).first()
        if not category:
            raise ValidationException("Category not found in this family")
        transaction.category_id = payload.category_id

    if payload.amount:
        transaction.amount = payload.amount
    if payload.description is not None:
        transaction.description = payload.description

    db.commit()
    db.refresh(transaction)

    return {
        "id": transaction.id,
        "family_id": transaction.family_id,
        "user_id": transaction.user_id,
        "user_name": transaction.user.full_name if transaction.user else None,
        "category_id": transaction.category_id,
        "category_name": transaction.category.name if transaction.category else None,
        "type": transaction.type,
        "amount": float(transaction.amount),
        "description": transaction.description,
        "transaction_date": transaction.transaction_date,
        "created_at": transaction.created_at,
        "updated_at": transaction.updated_at
    }

@router.delete("/families/{family_id}/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    family_id: int,
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_family_access(current_user.id, family_id, db)

    transaction = db.query(Transaction).filter(
        and_(Transaction.id == transaction_id, Transaction.family_id == family_id, Transaction.deleted_at == None)
    ).first()
    if not transaction:
        raise NotFoundException("Transaction not found")

    role = verify_family_access(current_user.id, family_id, db)
    is_author = transaction.user_id == current_user.id
    is_owner = role == "owner"

    if not (is_author or is_owner):
        raise ForbiddenException("Only author or owner can delete this transaction")

    from datetime import datetime
    transaction.deleted_at = datetime.utcnow()
    transaction.deleted_by = current_user.id
    db.commit()
