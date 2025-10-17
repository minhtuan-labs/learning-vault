from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
import models
from schemas.token import TokenData
from crud import crud_user


# Dòng này khởi tạo một "sơ đồ" bảo mật OAuth2.
# Nó chỉ cho FastAPI biết rằng token sẽ được lấy từ API endpoint nào.
# Client sẽ cần gửi một header dạng "Authorization: Bearer <your_token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    """
    Dependency này sẽ:
    1. Lấy token từ header Authorization.
    2. Giải mã token để lấy user_id.
    3. Lấy user từ database bằng user_id đó.
    4. Trả về đối tượng User model.
    Nếu có bất kỳ lỗi nào (token không hợp lệ, user không tồn tại),
    nó sẽ trả về lỗi 401 Unauthorized.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except (JWTError, ValueError):
        raise credentials_exception
    user = crud_user.get_user(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

