from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, get_db, Base
from app.routes import admin, auth, families, transactions, accounts, categories, dashboard
from app.models.user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

app = FastAPI(
    title="NestFi API",
    description="Family budgeting and transaction tracking API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
)

# Initialize database schema
init_db()

# Auto-seed database if empty
def seed_if_empty():
    from seed import seed_database
    try:
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        if session.query(User).count() == 0:
            seed_database()
        session.close()
    except Exception as e:
        print(f"Warning: Could not auto-seed database: {e}")

try:
    seed_if_empty()
except Exception:
    pass

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3100"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "message": "NestFi backend is running"}

# API routes
api_prefix = "/api/v1"
app.include_router(admin.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(families.router, prefix=api_prefix)
app.include_router(transactions.router, prefix=api_prefix)
app.include_router(accounts.router, prefix=api_prefix)
app.include_router(categories.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
