from fastapi import FastAPI
import models
from core.database import engine

from api.v1.endpoints import user as user_router
from api.v1.endpoints import asset as asset_router
from api.v1.endpoints import stock_portfolio as stock_portfolio_router
from api.v1.endpoints import stock_trade as stock_trade_router
from api.v1.endpoints import fund_portfolio as fund_portfolio_router
from api.v1.endpoints import fund_trade as fund_trade_router
from api.v1.endpoints import saving as saving_router
from api.v1.endpoints import transaction as transaction_router
from api.v1.endpoints import trades as trades_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
	title="P.A.M API",
	description="Private Asset Management API",
	version="0.1.0"
)


# Router cho Root
# @app.get("/", tags=["Root"])
def read_root():
	return {"message": "Welcome to PAM (Private Asset Management) API!"}


# Router for CRUD API
app.include_router(user_router.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(asset_router.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(stock_portfolio_router.router, prefix="/api/v1", tags=["Stock Portfolios"])
app.include_router(stock_trade_router.router, prefix="/api/v1", tags=["Stock Trades"])
app.include_router(fund_portfolio_router.router, prefix="/api/v1", tags=["Fund Portfolios"])
app.include_router(fund_trade_router.router, prefix="/api/v1", tags=["Fund Trades"])
app.include_router(saving_router.router, prefix="/api/v1", tags=["Savings"])
app.include_router(transaction_router.router, prefix="/api/v1", tags=["Transactions"])


# Router cho Business Action
app.include_router(trades_router.router, prefix="/api/v1/trades", tags=["Business Actions"])

