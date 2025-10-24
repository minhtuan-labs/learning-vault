from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
	# PostgreSQL Database Settings
	DB_USER: str = ""
	DB_PASSWORD: str = ""
	DB_HOST: str = ""
	DB_PORT: int = 5432
	DB_NAME: str = ""

	# Security settings
	PASSWORD_HASHING_ALGORITHM: str = "bcrypt"  # For password hashing
	PASSWORD_HASHING_DEPRECATED_SCHEMES: str = "auto"
	
	# JWT Token settings: run 'openssl rand -hex 32' for new SECRET_KEY
	JWT_SECRET_KEY: str = ""
	JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours (24 * 60 minutes)
	JWT_HASHING_ALGORITHM: str = "HS256"  # For JWT token signing
	
	# CORS settings
	BACKEND_CORS_ORIGINS: str = "http://localhost:6868,http://localhost:8501"
	
	@property
	def cors_origins_list(self) -> List[str]:
		"""Convert comma-separated CORS origins to list"""
		return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
	
	# API settings
	API_V1_STR: str = "/api/v1"
	PROJECT_NAME: str = "PAM - Private Asset Management"

	@property
	def DATABASE_URL(self) -> str:
		return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Single instance to be used across the application
settings = Settings()

