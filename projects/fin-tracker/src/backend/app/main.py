import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import Base, SessionLocal, engine
from app.models.company import Company  # noqa: F401
from app.models.financial import FinancialData, FinancialPeriod, ReportFile  # noqa: F401
from app.models.summary import CompanySummary  # noqa: F401
from app.models.setting import Setting  # noqa: F401
from app.models.user import User  # noqa: F401

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


def _seed_admin() -> None:
    from sqlalchemy import inspect as sa_inspect, text as sa_text

    db = SessionLocal()
    try:
        insp = sa_inspect(engine)
        col_names = {c["name"] for c in insp.get_columns("users")}
        if "is_admin" not in col_names:
            with engine.begin() as conn:
                conn.execute(sa_text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE"))

        if db.query(User).count() == 0:
            from app.services.auth_service import hash_password
            admin = User(
                username="admin",
                hashed_password=hash_password("admin"),
                display_name="Quản trị viên",
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
        elif not db.query(User).filter(User.is_admin.is_(True)).first():
            first_user = db.query(User).order_by(User.id).first()
            if first_user:
                first_user.is_admin = True
                first_user.is_active = True
                db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    for _ in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            time.sleep(2)
    Base.metadata.create_all(bind=engine)
    _seed_admin()


@app.get("/health")
def health_check():
    return {"status": "ok"}
