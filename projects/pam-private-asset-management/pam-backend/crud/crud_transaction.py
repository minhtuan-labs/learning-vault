from sqlalchemy.orm import Session

import models
from schemas.transaction import TransactionCreate, TransactionUpdate


def get_transaction(db: Session, transaction_id: int):
	return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()


def get_transactions_by_asset(db: Session, asset_id: int, skip: int = 0, limit: int = 100):
	return db.query(models.Transaction).filter(models.Transaction.asset_id == asset_id).offset(skip).limit(limit).all()


def create_asset_transaction(db: Session, transaction: TransactionCreate, asset_id: int):
	db_transaction = models.Transaction(
		**transaction.model_dump(),
		asset_id=asset_id
	)
	db.add(db_transaction)
	db.commit()
	db.refresh(db_transaction)
	return db_transaction


def update_transaction(db: Session, transaction_id: int, transaction_update: TransactionUpdate):
	db_transaction = get_transaction(db, transaction_id=transaction_id)
	if not db_transaction:
		return None
	update_data = transaction_update.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(db_transaction, key, value)
	db.add(db_transaction)
	db.commit()
	db.refresh(db_transaction)
	return db_transaction


def delete_transaction(db: Session, transaction_id: int):
	db_transaction = get_transaction(db, transaction_id=transaction_id)
	if not db_transaction:
		return None
	db.delete(db_transaction)
	db.commit()
	return db_transaction

