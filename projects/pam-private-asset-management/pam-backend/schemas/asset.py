from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from models.asset import AssetTypeEnum


class AssetBase(BaseModel):
	name: str
	asset_type: AssetTypeEnum


class AssetCreate(AssetBase):
	pass


class AssetUpdate(BaseModel):
	name: Optional[str] = None


class Asset(AssetBase):
	id: int
	cost_basis: float
	created_at: datetime
	owner_id: int

	model_config = ConfigDict(from_attributes=True)

