from sqlalchemy.orm import Session

from app.models.setting import DEFAULTS, Setting


def is_enabled(db: Session, key: str) -> bool:
    row = db.query(Setting).filter(Setting.key == key).first()
    value = row.value if row else DEFAULTS.get(key, {}).get("value", "true")
    return value.lower() in ("true", "1", "yes")