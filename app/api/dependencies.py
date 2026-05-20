# FastAPI dependency that provides a database session for each request.
# Using a dependency lets FastAPI automatically close the session when the request finishes.

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.database import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
    # Thin wrapper around the database module's get_db so routes import from here,
    # not directly from the db layer (makes overriding in tests easier).
    yield from _get_db()
