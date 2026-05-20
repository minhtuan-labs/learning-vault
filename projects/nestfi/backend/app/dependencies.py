from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
try:
    from fastapi.security import HTTPAuthCredentials
except ImportError:
    # Fallback for versions where HTTPAuthCredentials isn't directly available
    class HTTPAuthCredentials:
        def __init__(self, scheme: str, credentials: str):
            self.scheme = scheme
            self.credentials = credentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import decode_token
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
