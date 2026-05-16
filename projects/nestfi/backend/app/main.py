from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import engine
from app.models.base import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NestFi API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:8050"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
def health_check():
    from datetime import datetime
    return {
        "status": "ok",
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Import routes
from app.api.routes import auth, users, families, transactions, categories, analytics, admin
from app.api.routes import health

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(families.router, prefix="/families", tags=["families"])
app.include_router(transactions.router, tags=["transactions"])
app.include_router(categories.router, tags=["categories"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
