from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.transaction import Transaction, TransactionCreate, TransactionUpdate
from crud import crud_transaction, crud_asset
from api.v1.deps import get_current_user
from core.database import get_db
import models
from models.asset import AssetTypeEnum

router = APIRouter()

@router.post("/assets/{asset_id}/transactions/", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction_for_asset(
    asset_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_asset = crud_asset.get_asset(db, asset_id=asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if db_asset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this asset")
    if db_asset.asset_type != AssetTypeEnum.CASH:
        raise HTTPException(status_code=400, detail="Transactions can only be added to assets of type CASH")
    return crud_transaction.create_asset_transaction(db=db, transaction=transaction, asset_id=asset_id)


@router.get("/assets/{asset_id}/transactions/", response_model=List[Transaction])
def read_transactions_for_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    db_asset = crud_asset.get_asset(db, asset_id=asset_id)
    if not db_asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if db_asset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this asset")

    transactions = crud_transaction.get_transactions_by_asset(db, asset_id=asset_id, skip=skip, limit=limit)
    return transactions


@router.delete("/transactions/{transaction_id}", response_model=Transaction)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_transaction = crud_transaction.get_transaction(db, transaction_id=transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if db_transaction.asset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this transaction")

    return crud_transaction.delete_transaction(db, transaction_id=transaction_id)

