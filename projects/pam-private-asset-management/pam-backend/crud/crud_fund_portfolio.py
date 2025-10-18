from sqlalchemy.orm import Session

import models
from schemas.fund_portfolio import FundPortfolioCreate, FundPortfolioUpdate


def get_fund_portfolio(db: Session, portfolio_id: int):
	return db.query(models.FundPortfolio).filter(models.FundPortfolio.id == portfolio_id).first()


def get_fund_portfolios_by_asset(db: Session, asset_id: int, skip: int = 0, limit: int = 100):
	return db.query(models.FundPortfolio).filter(models.FundPortfolio.asset_id == asset_id).offset(skip).limit(
		limit).all()


def create_asset_fund_portfolio(db: Session, portfolio: FundPortfolioCreate, asset_id: int):
	existing_portfolio = db.query(models.FundPortfolio).filter(
		models.FundPortfolio.asset_id == asset_id,
		models.FundPortfolio.ticker == portfolio.ticker
	).first()
	if existing_portfolio:
		return None
	db_portfolio = models.FundPortfolio(
		**portfolio.model_dump(),
		asset_id=asset_id
	)
	db.add(db_portfolio)
	db.commit()
	db.refresh(db_portfolio)
	return db_portfolio


def update_fund_portfolio(db: Session, portfolio_id: int, portfolio_update: FundPortfolioUpdate):
	db_portfolio = get_fund_portfolio(db, portfolio_id=portfolio_id)
	if not db_portfolio:
		return None

	update_data = portfolio_update.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(db_portfolio, key, value)

	db.add(db_portfolio)
	db.commit()
	db.refresh(db_portfolio)
	return db_portfolio

