from sqlalchemy.orm import Session

import models
from schemas.asset import AssetCreate


def get_asset(db: Session, asset_id: int):
	return db.query(models.Asset).filter(models.Asset.id == asset_id).first()


def get_assets_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
	return db.query(models.Asset).filter(models.Asset.owner_id == owner_id).offset(skip).limit(limit).all()


def create_user_asset(db: Session, asset: AssetCreate, owner_id: int):
	db_asset = models.Asset(
		**asset.model_dump(),
		owner_id=owner_id
	)

	db.add(db_asset)
	db.commit()
	db.refresh(db_asset)

	return db_asset

