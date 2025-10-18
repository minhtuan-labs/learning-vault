from sqlalchemy.orm import Session

import models
from schemas.saving import SavingDetailCreate, SavingDetailUpdate


def get_saving_detail(db: Session, saving_id: int):
	return db.query(models.SavingDetail).filter(models.SavingDetail.id == saving_id).first()


def get_saving_detail_by_asset(db: Session, asset_id: int):
	return db.query(models.SavingDetail).filter(models.SavingDetail.asset_id == asset_id).first()


def create_asset_saving_detail(db: Session, saving: SavingDetailCreate, asset_id: int):
	db_saving = models.SavingDetail(
		**saving.model_dump(),
		asset_id=asset_id
	)
	db.add(db_saving)
	db.commit()
	db.refresh(db_saving)
	return db_saving


def update_saving_detail(db: Session, saving_id: int, saving_update: SavingDetailUpdate):
	db_saving = get_saving_detail(db, saving_id=saving_id)
	if not db_saving:
		return None
	update_data = saving_update.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(db_saving, key, value)

	db.add(db_saving)
	db.commit()
	db.refresh(db_saving)
	return db_saving


def delete_saving_detail(db: Session, saving_id: int):
	db_saving = get_saving_detail(db, saving_id=saving_id)
	if not db_saving:
		return None
	db.delete(db_saving)
	db.commit()
	return db_saving

