import logging
import sys
from core.config import settings

# Lấy cấp độ log từ file config, ví dụ "INFO" hoặc "WARNING"
log_level_str = settings.LOG_LEVEL.upper()
log_level = getattr(logging, log_level_str, logging.INFO)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str):
    return logging.getLogger(name)

