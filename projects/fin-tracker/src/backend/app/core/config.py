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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
