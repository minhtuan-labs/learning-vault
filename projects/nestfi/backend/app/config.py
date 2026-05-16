import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://nestfi:nestfi_password@localhost:5432/nestfi"
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@nestfi.local"

    api_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:8050"

    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
