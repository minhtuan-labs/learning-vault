from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_db_session
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import UserUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db_session), _admin: User = Depends(get_admin_user)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.put("/{user_id}/approve", response_model=UserResponse)
def approve_user(user_id: int, db: Session = Depends(get_db_session), _admin: User = Depends(get_admin_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: int, db: Session = Depends(get_db_session), _admin: User = Depends(get_admin_user)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    if target.id == _admin.id:
        raise HTTPException(status_code=400, detail="Không thể vô hiệu hóa chính mình.")
    target.is_active = False
    db.commit()
    db.refresh(target)
    return target


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdateRequest, db: Session = Depends(get_db_session), _admin: User = Depends(get_admin_user)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    if payload.is_admin is not None:
        if target.id == _admin.id and not payload.is_admin:
            raise HTTPException(status_code=400, detail="Không thể bỏ quyền quản trị của chính mình.")
        target.is_admin = payload.is_admin
    if payload.is_active is not None:
        if target.id == _admin.id and not payload.is_active:
            raise HTTPException(status_code=400, detail="Không thể vô hiệu hóa chính mình.")
        target.is_active = payload.is_active
    db.commit()
    db.refresh(target)
    return target


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db_session), _admin: User = Depends(get_admin_user)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    if target.id == _admin.id:
        raise HTTPException(status_code=400, detail="Không thể xoá chính mình.")
    db.delete(target)
    db.commit()