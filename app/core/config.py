from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Render/Heroku use postgres:// — SQLAlchemy needs postgresql+psycopg:// for psycopg v3."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://datads:datads@localhost:5433/datads"

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        return normalize_database_url(value)
    api_base_url: str = (
        "https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io"
    )
    facebook_api_key: str = "facebook_test_key_123"
    google_token: str = "google_test_token_456"
    tiktok_token: str = "tiktok_test_token_789"

    http_timeout_seconds: float = 30.0
    max_retry_attempts: int = 4


@lru_cache
def get_settings() -> Settings:
    return Settings()
