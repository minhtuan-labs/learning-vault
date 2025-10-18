from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas.fund_trade import FundTrade, FundTradeCreate, FundTradeUpdate
from crud import crud_fund_trade, crud_fund_portfolio
from api.v1.deps import get_current_user
from core.database import get_db
import models

router = APIRouter()


@router.post("/fund-portfolios/{portfolio_id}/fund-trades/", response_model=FundTrade,
			 status_code=status.HTTP_201_CREATED)
def create_fund_trade_for_portfolio(
		portfolio_id: int,
		trade: FundTradeCreate,
		cash_asset_id: int,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_portfolio = crud_fund_portfolio.get_fund_portfolio(db, portfolio_id=portfolio_id)
	if not db_portfolio:
		raise HTTPException(status_code=404, detail="Fund portfolio not found")
	if db_portfolio.asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to add trades to this portfolio")

	cash_asset = crud_asset.get_asset(db, asset_id=cash_asset_id)
	if not cash_asset:
		raise HTTPException(status_code=404, detail="Cash asset not found")
	if cash_asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to use this cash asset")
	if cash_asset.asset_type != AssetTypeEnum.CASH:
		raise HTTPException(status_code=400, detail="The specified asset for cash flow is not of type CASH")

	return crud_fund_trade.create_portfolio_fund_trade(
		db=db, trade=trade, portfolio_id=portfolio_id, cash_asset_id=cash_asset_id
	)


@router.patch("/fund-trades/{trade_id}", response_model=FundTrade)
def update_fund_trade(
		trade_id: int,
		trade_update: FundTradeUpdate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_trade = crud_fund_trade.get_fund_trade(db, trade_id=trade_id)
	if not db_trade:
		raise HTTPException(status_code=404, detail="Fund trade not found")
	if db_trade.portfolio.asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to update this trade")

	return crud_fund_trade.update_fund_trade(db, trade_id=trade_id, trade_update=trade_update)


@router.delete("/fund-trades/{trade_id}", response_model=FundTrade)
def delete_fund_trade(
		trade_id: int,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_trade = crud_fund_trade.get_fund_trade(db, trade_id=trade_id)
	if not db_trade:
		raise HTTPException(status_code=404, detail="Fund trade not found")
	if db_trade.portfolio.asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to delete this trade")

	return crud_fund_trade.delete_fund_trade(db, trade_id=trade_id)

