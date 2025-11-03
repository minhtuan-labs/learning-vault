from sqlalchemy.orm import Session

import models
from schemas.watchlist import WatchlistCreate, WatchlistUpdate


def get_watchlist(db: Session, watchlist_id: int):
	return db.query(models.Watchlist).filter(models.Watchlist.id == watchlist_id).first()


def get_watchlists_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
	return db.query(models.Watchlist).filter(
		models.Watchlist.owner_id == owner_id
	).offset(skip).limit(limit).all()


def get_watchlist_by_ticker(db: Session, owner_id: int, ticker: str):
	return db.query(models.Watchlist).filter(
		models.Watchlist.owner_id == owner_id,
		models.Watchlist.ticker == ticker.upper()
	).first()


def create_user_watchlist(db: Session, watchlist: WatchlistCreate, owner_id: int):
	# Kiểm tra đã tồn tại chưa
	existing = get_watchlist_by_ticker(db, owner_id, watchlist.ticker)
	if existing:
		return None
	
	# Lấy data và uppercase ticker
	watchlist_data = watchlist.model_dump()
	watchlist_data["ticker"] = watchlist.ticker.upper()
	watchlist_data["owner_id"] = owner_id
	
	db_watchlist = models.Watchlist(**watchlist_data)
	db.add(db_watchlist)
	db.commit()
	db.refresh(db_watchlist)
	return db_watchlist


def update_watchlist(db: Session, watchlist_id: int, watchlist_update: WatchlistUpdate):
	db_watchlist = get_watchlist(db, watchlist_id)
	if not db_watchlist:
		return None
	
	update_data = watchlist_update.model_dump(exclude_unset=True)
	for field, value in update_data.items():
		setattr(db_watchlist, field, value)
	
	db.commit()
	db.refresh(db_watchlist)
	return db_watchlist


def delete_watchlist(db: Session, watchlist_id: int):
	db_watchlist = get_watchlist(db, watchlist_id)
	if not db_watchlist:
		return None
	db.delete(db_watchlist)
	db.commit()
	return db_watchlist

