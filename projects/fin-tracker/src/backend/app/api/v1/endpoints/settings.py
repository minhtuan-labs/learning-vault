from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.models.setting import DEFAULTS, Setting
from app.models.user import User
from app.schemas.setting import SettingResponse, SettingUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=list[SettingResponse])
def list_settings(db: Session = Depends(get_db_session), _current_user: User = Depends(get_current_user)):
    existing = {s.key: s for s in db.query(Setting).all()}
    result = []
    for key, defaults in DEFAULTS.items():
        if key in existing:
            result.append(existing[key])
        else:
            row = Setting(
                key=key,
                value=defaults["value"],
                label=defaults["label"],
                description=defaults["description"],
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            result.append(row)
    return result


@router.put("/{key}", response_model=SettingResponse)
def update_setting(
    key: str,
    payload: SettingUpdate,
    db: Session = Depends(get_db_session),
    _current_user: User = Depends(get_current_user),
):
    if key not in DEFAULTS:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    row = db.query(Setting).filter(Setting.key == key).first()
    if not row:
        row = Setting(
            key=key,
            value=payload.value,
            label=DEFAULTS[key]["label"],
            description=DEFAULTS[key]["description"],
        )
        db.add(row)
    else:
        row.value = payload.value
    db.commit()
    db.refresh(row)
    return row