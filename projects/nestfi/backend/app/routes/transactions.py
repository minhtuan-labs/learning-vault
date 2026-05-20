from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionEdit
from app.models.family import Family, FamilyMembership, RoleEnum
from app.models.account import Account
from app.models.category import Category
from app.schemas.transaction import (
    TransactionSchema,
    TransactionListResponse,
    TransactionCreateRequest,
    TransactionUpdateRequest,
    TransactionToggleRequest,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/families", tags=["transactions"])


async def check_family_access(family_id: UUID, current_user: User, db: Session):
    family = db.query(Family).filter(Family.id == family_id).first()
    if family and not family.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Family is disabled")
    membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")
    return membership


def enrich_transaction(tx: Transaction, db: Session) -> TransactionSchema:
    category = db.query(Category).filter(Category.id == tx.category_id).first()
    account = db.query(Account).filter(Account.id == tx.account_id).first()
    return TransactionSchema(
        id=tx.id,
        account_id=tx.account_id,
        category_id=tx.category_id,
        category_name=category.name if category else None,
        account_name=account.name if account else None,
        amount_cents=tx.amount_cents,
        direction=tx.direction.value if hasattr(tx.direction, 'value') else tx.direction,
        date=tx.date,
        description=tx.description,
        creator_id=tx.creator_id,
        is_enabled=tx.is_enabled,
        created_at=tx.created_at,
        updated_at=tx.updated_at,
    )


@router.get("/{family_id}/accounts/{account_id}/transactions", response_model=TransactionListResponse)
async def list_transactions(
    family_id: UUID,
    account_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    await check_family_access(family_id, current_user, db)

    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.is_enabled == True
    ).offset(offset).limit(limit).all()

    total_count = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.is_enabled == True
    ).count()

    return TransactionListResponse(
        transactions=[enrich_transaction(tx, db) for tx in transactions],
        total_count=total_count,
        has_more=(offset + limit) < total_count
    )


@router.post("/{family_id}/accounts/{account_id}/transactions", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    family_id: UUID,
    account_id: UUID,
    request: TransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    await check_family_access(family_id, current_user, db)

    transaction = Transaction(
        account_id=account_id,
        category_id=request.category_id,
        amount_cents=request.amount_cents,
        direction=request.direction,
        date=request.date,
        description=request.description,
        creator_id=current_user.id,
        is_enabled=True
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return enrich_transaction(transaction, db)


@router.put("/{family_id}/accounts/{account_id}/transactions/{tx_id}")
async def update_transaction(
    family_id: UUID,
    account_id: UUID,
    tx_id: UUID,
    request: TransactionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await check_family_access(family_id, current_user, db)

    transaction = db.query(Transaction).filter(
        Transaction.id == tx_id,
        Transaction.account_id == account_id,
    ).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    before = {
        "amount_cents": transaction.amount_cents,
        "direction": transaction.direction.value if hasattr(transaction.direction, 'value') else transaction.direction,
        "date": transaction.date,
        "description": transaction.description,
        "category_id": str(transaction.category_id),
    }

    if request.amount_cents is not None:
        transaction.amount_cents = request.amount_cents
    if request.direction is not None:
        transaction.direction = request.direction
    if request.date is not None:
        transaction.date = request.date
    if request.description is not None:
        transaction.description = request.description
    if request.category_id is not None:
        transaction.category_id = request.category_id

    after = {
        "amount_cents": transaction.amount_cents,
        "direction": transaction.direction.value if hasattr(transaction.direction, 'value') else transaction.direction,
        "date": transaction.date,
        "description": transaction.description,
        "category_id": str(transaction.category_id),
    }

    edit = TransactionEdit(
        transaction_id=tx_id,
        editor_id=current_user.id,
        before_snapshot=before,
        after_snapshot=after,
    )
    db.add(edit)
    db.commit()
    db.refresh(transaction)

    return enrich_transaction(transaction, db)


@router.patch("/{family_id}/accounts/{account_id}/transactions/{tx_id}")
async def toggle_transaction(
    family_id: UUID,
    account_id: UUID,
    tx_id: UUID,
    request: TransactionToggleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    await check_family_access(family_id, current_user, db)

    transaction = db.query(Transaction).filter(
        Transaction.id == tx_id,
        Transaction.account_id == account_id,
    ).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    transaction.is_enabled = request.is_enabled
    db.commit()
    db.refresh(transaction)

    return {"id": str(transaction.id), "is_enabled": transaction.is_enabled}


@router.delete("/{family_id}/accounts/{account_id}/transactions/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    family_id: UUID,
    account_id: UUID,
    tx_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    family = db.query(Family).filter(Family.id == family_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")

    is_owner = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id,
        FamilyMembership.role == RoleEnum.owner,
    ).first()
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner only")

    transaction = db.query(Transaction).filter(
        Transaction.id == tx_id,
        Transaction.account_id == account_id,
    ).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    db.query(TransactionEdit).filter(TransactionEdit.transaction_id == tx_id).delete()
    db.delete(transaction)
    db.commit()

    return None
