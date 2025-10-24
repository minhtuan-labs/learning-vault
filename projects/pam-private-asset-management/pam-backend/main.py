from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from core.database import engine
from core.config import settings

from api.v1.endpoints import user as user_router
from api.v1.endpoints import asset as asset_router
from api.v1.endpoints import stock_portfolio as stock_portfolio_router
from api.v1.endpoints import stock_trade as stock_trade_router
from api.v1.endpoints import fund_portfolio as fund_portfolio_router
from api.v1.endpoints import fund_trade as fund_trade_router
from api.v1.endpoints import saving as saving_router
from api.v1.endpoints import transaction as transaction_router
from api.v1.endpoints import trades as trades_router

app = FastAPI(
	title=settings.PROJECT_NAME,
	description="Private Asset Management API",
	version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
	"""Create database tables on startup"""
	try:
		models.Base.metadata.create_all(bind=engine)
		print("✅ Database tables created successfully")
	except Exception as e:
		print(f"❌ Error creating database tables: {e}")
		raise

# CORS middleware
app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins_list,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
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

