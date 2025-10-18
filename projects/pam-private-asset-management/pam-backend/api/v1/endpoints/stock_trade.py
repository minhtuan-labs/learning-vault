from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas.stock_trade import StockTrade, StockTradeCreate, StockTradeUpdate
from crud import crud_stock_trade, crud_stock_portfolio
from api.v1.deps import get_current_user
from core.database import get_db
import models


router = APIRouter()


@router.post("/stock-portfolios/{portfolio_id}/stock-trades/", response_model=StockTrade,
			 status_code=status.HTTP_201_CREATED)
def create_stock_trade_for_portfolio(
		portfolio_id: int,
		trade: StockTradeCreate,
		cash_asset_id: int,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_portfolio = crud_stock_portfolio.get_stock_portfolio(db, portfolio_id=portfolio_id)
	if not db_portfolio:
		raise HTTPException(status_code=404, detail="Stock portfolio not found")
	if db_portfolio.asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to add trades to this portfolio")

	cash_asset = crud_asset.get_asset(db, asset_id=cash_asset_id)
	if not cash_asset:
		raise HTTPException(status_code=404, detail="Cash asset not found")
	if cash_asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to use this cash asset")
	if cash_asset.asset_type != AssetTypeEnum.CASH:
		raise HTTPException(status_code=400, detail="The specified asset for cash flow is not of type CASH")

	return crud_stock_trade.create_portfolio_stock_trade(
		db=db, trade=trade, portfolio_id=portfolio_id, cash_asset_id=cash_asset_id
	)


@router.patch("/stock-trades/{trade_id}", response_model=StockTrade)
def update_stock_trade(
		trade_id: int,
		trade_update: StockTradeUpdate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_trade = crud_stock_trade.get_stock_trade(db, trade_id=trade_id)
	if not db_trade:
		raise HTTPException(status_code=404, detail="Stock trade not found")
	# Kiểm tra quyền sở hữu thông qua portfolio cha
	if db_trade.portfolio.asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to update this trade")
	return crud_stock_trade.update_stock_trade(db, trade_id=trade_id, trade_update=trade_update)


@router.delete("/stock-trades/{trade_id}", response_model=StockTrade)
def delete_stock_trade(
		trade_id: int,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_trade = crud_stock_trade.get_stock_trade(db, trade_id=trade_id)
	if not db_trade:
		raise HTTPException(status_code=404, detail="Stock trade not found")
	if db_trade.portfolio.asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to delete this trade")
	return crud_stock_trade.delete_stock_trade(db, trade_id=trade_id)

