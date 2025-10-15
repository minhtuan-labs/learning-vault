from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import init_db
from app.api.v1.endpoints import users # <-- IMPORT THE NEW ROUTER

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    init_db()
    yield
    print("Application shutdown...")

app = FastAPI(
    title="P.A.M - Private Asset Management API",
    lifespan=lifespan
)

# Include the users router
# All routes from users.py will now be available under the /api/v1/users prefix
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to P.A.M API"}

