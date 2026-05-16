from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://datads:datads@localhost:5432/datads"
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
