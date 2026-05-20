# Tests for the database URL normalisation logic in app/core/config.py.
# Ensures the app works with URLs from Render, Heroku, and local Postgres.

from app.core.config import normalize_database_url


def test_normalize_render_postgres_url():
    # Render emits "postgres://" — must be rewritten for SQLAlchemy + psycopg v3.
    url = "postgres://user:pass@host.render.com:5432/dbname"
    assert normalize_database_url(url) == (
        "postgresql+psycopg://user:pass@host.render.com:5432/dbname"
    )


def test_normalize_postgresql_without_driver():
    # Plain "postgresql://" also needs the "+psycopg" driver suffix added.
    url = "postgresql://user:pass@localhost:5432/db"
    assert normalize_database_url(url) == "postgresql+psycopg://user:pass@localhost:5432/db"


def test_passthrough_psycopg_url():
    # Already-correct URLs should pass through unchanged.
    url = "postgresql+psycopg://datads:datads@localhost:5433/datads"
    assert normalize_database_url(url) == url
