from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.schemas.user import UserChangePassword
from app.models import User
from app.utils.security import hash_password, verify_password
from app.utils.exceptions import ValidationException

router = APIRouter()

@router.post("/change-password")
def change_password(
    payload: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise ValidationException("Current password is incorrect")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()

    return {"success": True, "message": "Password changed successfully"}
