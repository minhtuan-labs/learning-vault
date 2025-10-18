from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas.saving import SavingDetail, SavingDetailCreate, SavingDetailUpdate
from crud import crud_saving, crud_asset
from api.v1.deps import get_current_user
from core.database import get_db
import models
from models.asset import AssetTypeEnum

router = APIRouter()


@router.post("/assets/{asset_id}/savings/", response_model=SavingDetail, status_code=status.HTTP_201_CREATED)
def create_saving_detail(
		asset_id: int,
		saving: SavingDetailCreate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_asset = crud_asset.get_asset(db, asset_id=asset_id)
	if not db_asset:
		raise HTTPException(status_code=404, detail="Asset not found")
	if db_asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to access this asset")
	if db_asset.asset_type != AssetTypeEnum.SAVINGS:
		raise HTTPException(status_code=400, detail="Saving details can only be added to assets of type SAVINGS")
	existing_saving = crud_saving.get_saving_detail_by_asset(db, asset_id=asset_id)
	if existing_saving:
		raise HTTPException(status_code=400, detail="This asset already has a saving detail")
	return crud_saving.create_asset_saving_detail(db=db, saving=saving, asset_id=asset_id)


@router.patch("/savings/{saving_id}", response_model=SavingDetail)
def update_saving_detail(
		saving_id: int,
		saving_update: SavingDetailUpdate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_saving = crud_saving.get_saving_detail(db, saving_id=saving_id)
	if not db_saving:
		raise HTTPException(status_code=404, detail="Saving detail not found")
	if db_saving.asset.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to update this saving detail")
	return crud_saving.update_saving_detail(db, saving_id=saving_id, saving_update=saving_update)

