from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import các schema và crud cần thiết
from schemas.stock_trade import StockTrade, StockTradeCreate
from schemas.asset import AssetCreate
from schemas.stock_portfolio import StockPortfolioCreate
from crud import crud_asset, crud_stock_portfolio, crud_stock_trade
from api.v1.deps import get_current_user
from core.database import get_db
import models
from models.asset import AssetTypeEnum

router = APIRouter()


@router.post("/stock", response_model=StockTrade, status_code=status.HTTP_201_CREATED)
def record_stock_trade(
		trade: StockTradeCreate,
		ticker: str,
		# SỬA LỖI: Tham số `cash_asset_id` đã được loại bỏ khỏi đây
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	"""
	API nghiệp vụ để ghi nhận một giao dịch cổ phiếu.
	Hệ thống sẽ tự động tìm hoặc tạo các Asset cần thiết.
	"""
	# --- 1. Tìm hoặc tạo Asset loại STOCKS ---
	stock_asset = db.query(models.Asset).filter(
		models.Asset.owner_id == current_user.id,
		models.Asset.asset_type == AssetTypeEnum.STOCKS
	).first()
	if not stock_asset:
		stock_asset_schema = AssetCreate(name="Stock Holdings", asset_type=AssetTypeEnum.STOCKS)
		stock_asset = crud_asset.create_user_asset(db, asset=stock_asset_schema, owner_id=current_user.id)

	# --- 2. Tìm hoặc tạo StockPortfolio cho ticker ---
	stock_portfolio = db.query(models.StockPortfolio).filter(
		models.StockPortfolio.asset_id == stock_asset.id,
		models.StockPortfolio.ticker == ticker.upper()
	).first()
	if not stock_portfolio:
		portfolio_schema = StockPortfolioCreate(ticker=ticker.upper())
		stock_portfolio = crud_stock_portfolio.create_asset_stock_portfolio(
			db, portfolio=portfolio_schema, asset_id=stock_asset.id
		)

	# --- 3. Tự động tìm hoặc tạo Asset tiền mặt ---
	cash_asset = db.query(models.Asset).filter(
		models.Asset.owner_id == current_user.id,
		models.Asset.asset_type == AssetTypeEnum.CASH
	).first()
	if not cash_asset:
		cash_asset_schema = AssetCreate(name="Investment Cash", asset_type=AssetTypeEnum.CASH)
		cash_asset = crud_asset.create_user_asset(db, asset=cash_asset_schema, owner_id=current_user.id)

	# --- 4. Gọi CRUD để tạo giao dịch (logic tự động hóa dòng tiền đã có sẵn) ---
	return crud_stock_trade.create_portfolio_stock_trade(
		db=db, trade=trade, portfolio_id=stock_portfolio.id, cash_asset_id=cash_asset.id
	)


@router.get("/stock", response_model=List[StockTrade])
def get_all_stock_trades(
	db: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_user)
):
	"""
	Lấy toàn bộ lịch sử giao dịch cổ phiếu của người dùng.
	"""
	trades = (
		db.query(models.StockTrade)
		.join(models.StockPortfolio)
		.join(models.Asset)
		.filter(models.Asset.owner_id == current_user.id)
		.order_by(models.StockTrade.trade_date.desc())
		.all()
	)
	return trades
