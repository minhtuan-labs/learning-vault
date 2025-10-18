from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.fund_portfolio import FundPortfolio, FundPortfolioCreate, FundPortfolioUpdate
from crud import crud_fund_portfolio, crud_asset
from api.v1.deps import get_current_user
from core.database import get_db
import models

router = APIRouter()


@router.post("/assets/{asset_id}/fund-portfolios/", response_model=FundPortfolio, status_code=status.HTTP_201_CREATED)
def create_fund_portfolio(
		asset_id: int,
		portfolio: FundPortfolioCreate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_asset = crud_asset.get_asset(db, asset_id=asset_id)
	if not db_asset:
		raise HTTPException(status_code=404, detail="Asset not found")
	if db_asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to access this asset")

	db_portfolio = crud_fund_portfolio.create_asset_fund_portfolio(db=db, portfolio=portfolio, asset_id=asset_id)
	if db_portfolio is None:
		raise HTTPException(status_code=400, detail=f"Ticker '{portfolio.ticker}' already exists in this asset")

	return db_portfolio


@router.get("/assets/{asset_id}/fund-portfolios/", response_model=List[FundPortfolio])
def read_fund_portfolios(
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

	portfolios = crud_fund_portfolio.get_fund_portfolios_by_asset(db, asset_id=asset_id, skip=skip, limit=limit)
	return portfolios


@router.patch("/fund-portfolios/{portfolio_id}", response_model=FundPortfolio)
def update_fund_portfolio(
		portfolio_id: int,
		portfolio_update: FundPortfolioUpdate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_portfolio = crud_fund_portfolio.get_fund_portfolio(db, portfolio_id=portfolio_id)
	if not db_portfolio:
		raise HTTPException(status_code=404, detail="Fund portfolio not found")
	if db_portfolio.asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to update this portfolio")

	return crud_fund_portfolio.update_fund_portfolio(db, portfolio_id=portfolio_id, portfolio_update=portfolio_update)

