from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.utils.security import decode_token
from app.utils.exceptions import UnauthorizedException
from typing import Optional

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(authorization: Optional[str] = None, db: Session = Depends(get_db)):
    if not authorization:
        raise UnauthorizedException()

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise UnauthorizedException()
    except ValueError:
        raise UnauthorizedException()

    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException()

    from app.models import User
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException()

    return user
