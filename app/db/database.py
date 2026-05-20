# Database engine and session factory.
# Everything that needs a DB connection imports SessionLocal or get_db from here.

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# pool_pre_ping=True sends a cheap "SELECT 1" before each connection to drop stale ones.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# autocommit=False means we must commit explicitly; autoflush=False avoids surprise queries.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All ORM models inherit from Base so Alembic can discover them for migrations.
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    # Open a session, yield it to the caller, and always close it afterwards.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
