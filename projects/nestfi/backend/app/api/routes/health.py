from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
