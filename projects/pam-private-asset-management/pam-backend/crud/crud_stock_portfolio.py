from sqlalchemy.orm import Session

import models
from schemas.stock_portfolio import StockPortfolioCreate, StockPortfolioUpdate


def get_stock_portfolio(db: Session, portfolio_id: int):
	return db.query(models.StockPortfolio).filter(models.StockPortfolio.id == portfolio_id).first()


def get_stock_portfolios_by_asset(db: Session, asset_id: int, skip: int = 0, limit: int = 100):
	return db.query(models.StockPortfolio).filter(models.StockPortfolio.asset_id == asset_id).offset(skip).limit(limit).all()


def get_stock_portfolio_by_ticker_and_owner(db: Session, ticker: str, owner_id: int):
	"""Get stock portfolio by ticker and owner_id"""
	return db.query(models.StockPortfolio).join(models.Asset).filter(
		models.StockPortfolio.ticker == ticker.upper(),
		models.Asset.owner_id == owner_id
	).first()


def create_asset_stock_portfolio(db: Session, portfolio: StockPortfolioCreate, asset_id: int):
	existing_portfolio = db.query(models.StockPortfolio).filter(
		models.StockPortfolio.asset_id == asset_id,
		models.StockPortfolio.ticker == portfolio.ticker
	).first()
	if existing_portfolio:
		return None
	db_portfolio = models.StockPortfolio(
		**portfolio.model_dump(),
		asset_id=asset_id
	)
	db.add(db_portfolio)
	db.commit()
	db.refresh(db_portfolio)
	return db_portfolio


def update_stock_portfolio(db: Session, portfolio_id: int, portfolio_update: StockPortfolioUpdate):
	db_portfolio = get_stock_portfolio(db, portfolio_id=portfolio_id)
	if not db_portfolio:
		return None
	update_data = portfolio_update.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(db_portfolio, key, value)
	db.add(db_portfolio)
	db.commit()
	db.refresh(db_portfolio)
	return db_portfolio

