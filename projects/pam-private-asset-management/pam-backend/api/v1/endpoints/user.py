from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas.user import User, UserCreate
from crud import crud_user
from core.database import SessionLocal, get_db
from schemas.token import Token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Xác thực user và trả về một access token.
    FastAPI sẽ tự động lấy username và password từ body của request
    khi client gửi request với content-type là 'application/x-www-form-urlencoded'.
    """
    # 1. Tìm user trong DB bằng username
    user = crud_user.get_user_by_username(db, username=form_data.username)

    # 2. Kiểm tra user có tồn tại không và mật khẩu có đúng không
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Tạo access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    # 4. Trả về token cho client
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
	"""
	Tạo một user mới.
	"""
	db_user = crud_user.get_user_by_username(db, username=user.username)
	if db_user:
		raise HTTPException(status_code=400, detail="Username already registered")

	return crud_user.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
	"""
	Lấy thông tin của một user bằng ID.
	"""
	db_user = crud_user.get_user(db, user_id=user_id)
	if db_user is None:
		raise HTTPException(status_code=404, detail="User not found")
	return db_user

