from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	PAM_BACKEND_API_URL: str = "http://localhost:8000"

settings = Settings()

