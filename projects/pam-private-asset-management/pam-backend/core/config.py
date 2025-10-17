from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	# PostgreSQL Database Settings
	DB_USER: str = ""
	DB_PASSWORD: str = ""
	DB_HOST: str = ""
	DB_PORT: int = 5432
	DB_NAME: str = ""

	# Security settings
	PASSWORD_HASHING_ALGORITHM: str = "sha256"
	PASSWORD_HASHING_DEPRECATED_SCHEMES: str = "strict"

	# JWT Token settings: run 'openssl rand -hex 32' for new SECRET_KEY
	JWT_SECRET_KEY: str = ""
	JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
	JWT_HASHING_ALGORITHM: str = "sha256"

	@property
	def DATABASE_URL(self) -> str:
		return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Single instance to be used across the application
settings = Settings()

