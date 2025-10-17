from sqlalchemy.orm import Session

import models
from schemas.stock_trade import StockTradeCreate, StockTradeUpdate


def get_stock_trade(db: Session, trade_id: int):
	return db.query(models.StockTrade).filter(models.StockTrade.id == trade_id).first()


def create_portfolio_stock_trade(db: Session, trade: StockTradeCreate, portfolio_id: int):
	db_trade = models.StockTrade(**trade.model_dump(), portfolio_id=portfolio_id)
	db.add(db_trade)
	db.commit()
	db.refresh(db_trade)
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

