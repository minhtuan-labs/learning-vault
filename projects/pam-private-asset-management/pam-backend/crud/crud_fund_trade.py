from sqlalchemy.orm import Session

import models
from schemas.fund_trade import FundTradeCreate, FundTradeUpdate
from . import crud_transaction
from schemas.transaction import TransactionCreate
from models.transaction import TransactionTypeEnum
from models.fund_trade import FundTradeTypeEnum


def get_fund_trade(db: Session, trade_id: int):
	return db.query(models.FundTrade).filter(models.FundTrade.id == trade_id).first()


def create_portfolio_fund_trade(db: Session, trade: FundTradeCreate, portfolio_id: int):
	db_trade = models.FundTrade(
		**trade.model_dump(),
		portfolio_id=portfolio_id
	)
	db.add(db_trade)
	db.commit()
	db.refresh(db_trade)

	if trade.trade_type == FundTradeTypeEnum.BUY:
		transaction_type = TransactionTypeEnum.FUND_BUY
		transaction_amount = -(total_amount + trade.fee)
	elif trade.trade_type == FundTradeTypeEnum.SELL:
		transaction_type = TransactionTypeEnum.FUND_SELL
		transaction_amount = total_amount - trade.fee

	if transaction_type:
		transaction_schema = TransactionCreate(
			amount=transaction_amount,
			transaction_type=transaction_type,
			transaction_date=trade.trade_date,
			description=f"{trade.trade_type.value.upper()} {trade.quantity} units of {db_trade.portfolio.ticker} @ {trade.price}"
		)
		crud_transaction.create_asset_transaction(
			db=db, transaction=transaction_schema, asset_id=cash_asset_id
		)

	return db_trade


def update_fund_trade(db: Session, trade_id: int, trade_update: FundTradeUpdate):
	db_trade = get_fund_trade(db, trade_id=trade_id)
	if not db_trade:
		return None
	update_data = trade_update.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(db_trade, key, value)
	db.add(db_trade)
	db.commit()
	db.refresh(db_trade)
	return db_trade


def delete_fund_trade(db: Session, trade_id: int):
	db_trade = get_fund_trade(db, trade_id=trade_id)
	if not db_trade:
		return None
	db.delete(db_trade)
	db.commit()
	return db_trade

