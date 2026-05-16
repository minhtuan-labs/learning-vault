from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.schemas.user import UserLogin, LoginResponse, UserResponse
from app.models import User
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.exceptions import UnauthorizedException
from datetime import timedelta

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")

    access_token = create_access_token({"sub": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user).dict()
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)
