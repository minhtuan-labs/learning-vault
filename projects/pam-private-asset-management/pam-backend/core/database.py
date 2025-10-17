from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# --- PostgreSQL Configuration ---
# Driver required: pip install psycopg2-binary

# Get the pre-built database URL from the settings object
SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

