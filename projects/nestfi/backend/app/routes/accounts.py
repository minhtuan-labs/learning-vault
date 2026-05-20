from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from uuid import UUID
import uuid as uuid_mod

from app.database import get_db
from app.models.user import User
from app.models.account import Account, AccountTypeEnum
from app.models.transaction import Transaction, DirectionEnum
from app.models.family import Family, FamilyMembership
from app.schemas.account import (
    AccountSchema,
    AccountListResponse,
    AccountCreateRequest,
    AccountUpdateRequest,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/families", tags=["accounts"])


def _check_family_member(family_id: UUID, current_user: User, db: Session):
    family = db.query(Family).filter(Family.id == family_id).first()
    if family and not family.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Family is disabled")
    membership = db.query(FamilyMembership).filter(
        FamilyMembership.family_id == family_id,
        FamilyMembership.user_id == current_user.id,
    ).first()
    if not membership and not current_user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")
    return membership


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


@router.get("/{family_id}/accounts", response_model=AccountListResponse)
async def list_accounts(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_family_member(family_id, current_user, db)
    accounts = db.query(Account).filter(Account.family_id == family_id).all()
    return AccountListResponse(
        accounts=[
            AccountSchema(
                id=a.id,
                name=a.name,
                type=a.type.value,
                balance_cents=_compute_balance(a, db),
                currency=a.currency,
                created_at=a.created_at,
            )
            for a in accounts
        ]
    )


@router.post("/{family_id}/accounts", status_code=status.HTTP_201_CREATED)
async def create_account(
    family_id: UUID,
    request: AccountCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_family_member(family_id, current_user, db)

    try:
        acct_type = AccountTypeEnum(request.type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid account type: {request.type}",
        )

    account = Account(
        id=uuid_mod.uuid4(),
        family_id=family_id,
        name=request.name,
        type=acct_type,
        balance_cents=request.initial_balance_cents,
        currency=request.currency,
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    return AccountSchema(
        id=account.id,
        name=account.name,
        type=account.type.value,
        balance_cents=account.balance_cents,
        currency=account.currency,
        created_at=account.created_at,
    )


@router.put("/{family_id}/accounts/{account_id}")
async def update_account(
    family_id: UUID,
    account_id: UUID,
    request: AccountUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_family_member(family_id, current_user, db)

    account = db.query(Account).filter(
        Account.id == account_id,
        Account.family_id == family_id,
    ).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if request.name is not None:
        account.name = request.name
    if request.type is not None:
        try:
            account.type = AccountTypeEnum(request.type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid account type: {request.type}",
            )

    db.commit()
    db.refresh(account)

    return AccountSchema(
        id=account.id,
        name=account.name,
        type=account.type.value,
        balance_cents=_compute_balance(account, db),
        currency=account.currency,
        created_at=account.created_at,
    )
