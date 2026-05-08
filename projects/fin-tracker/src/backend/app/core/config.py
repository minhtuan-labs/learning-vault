from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "fin-tracker API"
    environment: str = "development"
    api_prefix: str = "/api"
    postgres_user: str = "fin_user"
    postgres_password: str = "fin_password"
    postgres_db: str = "fin_tracker"
    postgres_host: str = "db"
    postgres_port: int = 5432

    upload_dir: str = "/app/uploads"
    max_upload_mb: int = 50
    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"

    jwt_secret_key: str = "change-me-in-production"
    jwt_expire_hours: int = 24

    # Extra fields from .env (not used by backend but needed for pydantic)
    backend_port: int = 8000
    frontend_port: int = 3000
    vite_api_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
