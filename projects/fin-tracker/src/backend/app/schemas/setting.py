from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SettingResponse(BaseModel):
    key: str
    value: str
    label: str
    description: str | None
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SettingUpdate(BaseModel):
    value: str