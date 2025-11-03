from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.watchlist import Watchlist, WatchlistCreate, WatchlistUpdate
from crud import crud_watchlist
from api.v1.deps import get_current_user
from core.database import get_db
import models


router = APIRouter()


@router.post("/watchlists/", response_model=Watchlist, status_code=status.HTTP_201_CREATED)
def create_watchlist(
		watchlist: WatchlistCreate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_watchlist = crud_watchlist.create_user_watchlist(db=db, watchlist=watchlist, owner_id=current_user.id)
	if db_watchlist is None:
		raise HTTPException(status_code=400, detail=f"Ticker '{watchlist.ticker}' already exists in watchlist")
	return db_watchlist


@router.get("/watchlists/", response_model=List[Watchlist])
def read_watchlists(
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user),
		skip: int = 0,
		limit: int = 100
):
	watchlists = crud_watchlist.get_watchlists_by_owner(
		db, owner_id=current_user.id, skip=skip, limit=limit
	)
	return watchlists


@router.get("/watchlists/{watchlist_id}", response_model=Watchlist)
def read_watchlist(
		watchlist_id: int,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_watchlist = crud_watchlist.get_watchlist(db, watchlist_id=watchlist_id)
	if not db_watchlist:
		raise HTTPException(status_code=404, detail="Watchlist not found")
	if db_watchlist.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to access this watchlist")
	return db_watchlist


@router.patch("/watchlists/{watchlist_id}", response_model=Watchlist)
def update_watchlist(
		watchlist_id: int,
		watchlist_update: WatchlistUpdate,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_watchlist = crud_watchlist.get_watchlist(db, watchlist_id=watchlist_id)
	if not db_watchlist:
		raise HTTPException(status_code=404, detail="Watchlist not found")
	if db_watchlist.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to update this watchlist")
	return crud_watchlist.update_watchlist(db, watchlist_id=watchlist_id, watchlist_update=watchlist_update)


@router.delete("/watchlists/{watchlist_id}", response_model=Watchlist)
def delete_watchlist(
		watchlist_id: int,
		db: Session = Depends(get_db),
		current_user: models.User = Depends(get_current_user)
):
	db_watchlist = crud_watchlist.get_watchlist(db, watchlist_id=watchlist_id)
	if not db_watchlist:
		raise HTTPException(status_code=404, detail="Watchlist not found")
	if db_watchlist.owner_id != current_user.id:
		raise HTTPException(status_code=403, detail="Not authorized to delete this watchlist")
	return crud_watchlist.delete_watchlist(db, watchlist_id=watchlist_id)


