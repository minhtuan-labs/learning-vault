from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import user as user_crud
from app.schemas import user as user_schemas
from app.api.deps import get_db

router = APIRouter()

@router.post("/", response_model=user_schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
	db_user = user_crud.get_user_by_username(db, username=user.username)
	if db_user:
		raise HTTPException(
			status_code=400,
			detail="Username already registered"
		)
	return user_crud.create_user(db=db, user=user)


@router.get("/", response_model=List[user_schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	users = user_crud.get_users(db, skip=skip, limit=limit)
	return users


@router.get("/{user_id}", response_model=user_schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
	db_user = user_crud.get_user(db, user_id=user_id)
	if db_user is None:
		raise HTTPException(status_code=404, detail="User not found")
	return db_user

