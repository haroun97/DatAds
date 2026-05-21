# Application settings loaded from environment variables / .env file.
# All config values have safe defaults so the app can run locally without extra setup.

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Render/Heroku use postgres:// — SQLAlchemy needs postgresql+psycopg:// for psycopg v3."""
    # Rewrite legacy "postgres://" URLs that cloud platforms emit to the format
    # SQLAlchemy v2 + psycopg v3 require.
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    # Reads values from .env automatically; unknown keys are silently ignored.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Default points to the local Docker Postgres started by docker-compose.
    database_url: str = "postgresql+psycopg://datads:datads@localhost:5433/datads"

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        # Automatically fix the URL format before it reaches SQLAlchemy.
        return normalize_database_url(value)

    # Base URL for the mock ad-platform API used in development/tests.
    api_base_url: str = (
        "https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io"
    )

    # Platform API credentials — overridden via .env in real deployments.
    facebook_api_key: str = "facebook_test_key_123"
    google_token: str = "google_test_token_456"
    tiktok_token: str = "tiktok_test_token_789"

    # HTTP client behaviour.
    http_timeout_seconds: float = 30.0
    max_retry_attempts: int = 4

    # AWS / SQS settings — only required when running the background worker.
    aws_region: str = "eu-central-1"
    sqs_queue_url: str = ""   # must be set in .env for the worker to start
    sqs_dlq_url: str = ""
    sqs_wait_time_seconds: int = 20   # long-polling window in seconds
    sqs_max_messages: int = 1         # process one message at a time for simplicity

    # Comma-separated browser origins allowed to call the API (presentation site, local dev).
    cors_origins: str = (
        "http://localhost:8080,http://localhost:5173,http://localhost:3000,"
        "http://127.0.0.1:8080,http://127.0.0.1:5173,http://127.0.0.1:3000"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


# Cache the settings object so .env is only read once per process.
@lru_cache
def get_settings() -> Settings:
    return Settings()
