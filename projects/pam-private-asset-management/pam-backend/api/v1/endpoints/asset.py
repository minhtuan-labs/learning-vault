from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
from schemas.asset import Asset, AssetCreate
from crud import crud_asset
from api.v1.deps import get_current_user
from core.database import get_db

router = APIRouter()


@router.post("/", response_model=Asset)
def create_asset_for_current_user(
		asset: AssetCreate,
		db: Session = Depends(get_db),
		# "Tiêm" dependency vào đây. FastAPI sẽ tự động gọi hàm get_current_user
		# và gán kết quả (đối tượng User model) vào biến current_user.
		current_user: models.User = Depends(get_current_user)
):
	"""
	Tạo một asset mới cho user đang đăng nhập.
	"""
	# Sử dụng ID của user thật đã được xác thực từ token
	return crud_asset.create_user_asset(db=db, asset=asset, owner_id=current_user.id)


@router.get("/", response_model=List[Asset])
def read_assets_for_current_user(
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user),
		skip: int = 0,
		limit: int = 100
):
	"""
	Lấy danh sách các asset của user đang đăng nhập.
	"""
	assets = crud_asset.get_assets_by_owner(
		db, owner_id=current_user.id, skip=skip, limit=limit
	)
	return assets


@router.get("/{asset_id}", response_model=Asset)
def read_asset(
		asset_id: int,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	"""
	Lấy thông tin chi tiết của một asset bằng ID,
	chỉ khi asset đó thuộc về user đang đăng nhập.
	"""
	db_asset = crud_asset.get_asset(db, asset_id=asset_id)
	if db_asset is None:
		raise HTTPException(status_code=404, detail="Asset not found")

	# Kiểm tra bảo mật: đảm bảo user chỉ có thể xem asset của chính mình
	if db_asset.owner_id != current_user.id:
		raise HTTPException(
			status_code=403, detail="Not authorized to access this asset"
		)

	return db_asset

