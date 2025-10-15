from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext

from app.db.models.user import User as DBUser  # Import SQLAlchemy model
from app.schemas.user import UserCreate, UserUpdate  # Import Pydantic schemas

# Password hashing context (used for hashing/verifying passwords)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Helper functions for password hashing ---
def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


# --- CRUD Operations for User ---

# Get a user by ID
def get_user(db: Session, user_id: int):
	return db.query(DBUser).filter(DBUser.id == user_id).first()


# Get a user by username
def get_user_by_username(db: Session, username: str):
	return db.query(DBUser).filter(DBUser.username == username).first()


# Get multiple users (with skip and limit for pagination)
def get_users(db: Session, skip: int = 0, limit: int = 100):
	return db.query(DBUser).offset(skip).limit(limit).all()


# Create a new user
def create_user(db: Session, user: UserCreate):
	# Hash the password before storing it
	hashed_password = get_password_hash(user.password)

	# Create a new SQLAlchemy model instance
	db_user = DBUser(username=user.username, hashed_password=hashed_password)

	db.add(db_user)  # Add the new user to the session
	db.commit()  # Commit the transaction to save to DB
	db.refresh(db_user)  # Refresh the instance to get updated data (e.g., id)
	return db_user


# Update an existing user
def update_user(db: Session, db_user: DBUser, user_update: UserUpdate):
	# Update fields only if they are provided in the update schema
	if user_update.username is not None:
		db_user.username = user_update.username
	if user_update.password is not None:
		db_user.hashed_password = get_password_hash(user_update.password)

	db.commit()
	db.refresh(db_user)
	return db_user


# Delete a user
def delete_user(db: Session, user_id: int):
	db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
	if db_user:
		db.delete(db_user)
		db.commit()
		return db_user  # Return the deleted user, or True/False
	return None

