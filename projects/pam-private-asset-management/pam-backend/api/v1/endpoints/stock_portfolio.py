from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.stock_portfolio import StockPortfolio, StockPortfolioCreate, StockPortfolioUpdate
from crud import crud_stock_portfolio, crud_asset
from api.v1.deps import get_current_user
from core.database import get_db
import models


router = APIRouter()


@router.post("/assets/{asset_id}/stock-portfolios/", response_model=StockPortfolio, status_code=status.HTTP_201_CREATED)
def create_stock_portfolio(
		asset_id: int,
		portfolio: StockPortfolioCreate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_asset = crud_asset.get_asset(db, asset_id=asset_id)
	if not db_asset:
		raise HTTPException(status_code=404, detail="Asset not found")
	if db_asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to access this asset")
	db_portfolio = crud_stock_portfolio.create_asset_stock_portfolio(db=db, portfolio=portfolio, asset_id=asset_id)
	if db_portfolio is None:
		raise HTTPException(status_code=400, detail=f"Ticker '{portfolio.ticker}' already exists in this asset")
	return db_portfolio


@router.get("/assets/{asset_id}/stock-portfolios/", response_model=List[StockPortfolio])
def read_stock_portfolios(
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
	portfolios = crud_stock_portfolio.get_stock_portfolios_by_asset(db, asset_id=asset_id, skip=skip, limit=limit)
	return portfolios


@router.patch("/stock-portfolios/{portfolio_id}", response_model=StockPortfolio)
def update_stock_portfolio(
		portfolio_id: int,
		portfolio_update: StockPortfolioUpdate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_portfolio = crud_stock_portfolio.get_stock_portfolio(db, portfolio_id=portfolio_id)
	if not db_portfolio:
		raise HTTPException(status_code=404, detail="Stock portfolio not found")
	if db_portfolio.asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to update this portfolio")
	return crud_stock_portfolio.update_stock_portfolio(db, portfolio_id=portfolio_id, portfolio_update=portfolio_update)

