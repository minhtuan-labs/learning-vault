from sqlalchemy.orm import Session

import models
from schemas.stock_trade import StockTradeCreate, StockTradeUpdate
from . import crud_transaction
from schemas.transaction import TransactionCreate
from models.transaction import TransactionTypeEnum
from models.stock_trade import StockTradeTypeEnum


def get_stock_trade(db: Session, trade_id: int):
	return db.query(models.StockTrade).filter(models.StockTrade.id == trade_id).first()


def create_portfolio_stock_trade(db: Session, trade: StockTradeCreate, portfolio_id: int, cash_asset_id: int):
	db_trade = models.StockTrade(**trade.model_dump(), portfolio_id=portfolio_id)
	db.add(db_trade)
	db.commit()
	db.refresh(db_trade)

	total_amount = trade.quantity * trade.price
	transaction_type = None
	transaction_amount = 0

	if trade.trade_type == StockTradeTypeEnum.BUY:
		transaction_type = TransactionTypeEnum.STOCK_BUY
		transaction_amount = -(total_amount + trade.fee)
	elif trade.trade_type == StockTradeTypeEnum.SELL:
		transaction_type = TransactionTypeEnum.STOCK_SELL
		transaction_amount = total_amount - trade.fee

	if transaction_type:
		transaction_schema = TransactionCreate(
			amount=transaction_amount,
			transaction_type=transaction_type,
			transaction_date=trade.trade_date,
			description=f"{trade.trade_type.value.upper()} {trade.quantity} shares of {db_trade.portfolio.ticker} @ {trade.price}"
		)
		crud_transaction.create_asset_transaction(
			db=db, transaction=transaction_schema, asset_id=cash_asset_id
		)

	return db_trade


def update_stock_trade(db: Session, trade_id: int, trade_update: StockTradeUpdate):
	db_trade = get_stock_trade(db, trade_id=trade_id)
	if not db_trade:
		return None
	update_data = trade_update.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(db_trade, key, value)
	db.add(db_trade)
	db.commit()
	db.refresh(db_trade)
	return db_trade


def delete_stock_trade(db: Session, trade_id: int):
	db_trade = get_stock_trade(db, trade_id=trade_id)
	if not db_trade:
		return None
	db.delete(db_trade)
	db.commit()
	return db_trade

