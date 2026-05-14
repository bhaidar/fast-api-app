from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://fastapi:fastapi@127.0.0.1:5432/fastapi_app"
)


class Settings(BaseSettings):
    database_url: str = DEFAULT_DATABASE_URL

    model_config = SettingsConfigDict(
        env_file=".env.postgres",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
