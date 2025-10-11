import os
from pydantic_settings import BaseSettings

# Thêm thư mục gốc vào sys.path để Streamlit có thể tìm thấy module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
	BACKEND_URL_BASE: str = "http://tinyrag-backend:8000/api/v1"
	PAGE_SIZE: int = 10
	MODEL_NAME: str = "local-model"

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"

settings = Settings()
