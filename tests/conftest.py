# Shared pytest fixtures used across all test files.
# Uses an in-memory SQLite database so tests are fast, isolated, and need no external DB.

import os

# Override the database URL before any app modules are imported so they use SQLite.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.db.database import Base
from app.main import app


@pytest.fixture
def db_session():
    # Create a fresh in-memory SQLite DB for each test function.
    # StaticPool ensures the same in-memory DB is reused within a single test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)   # clean up so tests don't share state


@pytest.fixture
def client(db_session):
    # Override the FastAPI DB dependency so HTTP tests use the same in-memory session
    # as the db_session fixture — changes made via the API are visible in the fixture and vice versa.
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
