from fastapi import FastAPI
import models
from core.database import engine

from api.v1.endpoints import user as user_router
from api.v1.endpoints import asset as asset_router

models.Base.metadata.create_all(bind=engine)


app = FastAPI(
	title="P.A.M API",
	description="Private Asset Management API",
	version="0.1.0"
)


@app.get("/", tags=["Root"])
def read_root():
	return {"message": "Welcome to PAM (Private Asset Management) API!"}


app.include_router(
    user_router.router,
    prefix="/api/v1/users",
    tags=["Users"]
)


app.include_router(
    asset_router.router,
    prefix="/api/v1/assets",
    tags=["Assets"]
)


app.include_router(
    stock_portfolio_router.router,
    prefix="/api/v1", # Tiền tố chung, vì các URL đầy đủ đã được định nghĩa trong file endpoint
    tags=["Stock Portfolios"]
)


app.include_router(
    stock_trade_router.router,
    prefix="/api/v1", # Tiền tố chung
    tags=["Stock Trades"]
)

