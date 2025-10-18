from sqlalchemy.orm import Session

import models
from schemas.fund_trade import FundTradeCreate, FundTradeUpdate


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

