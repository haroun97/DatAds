from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.ingest_job import IngestCampaignJob, IngestPlatformJob
from app.worker.processor import JobProcessor


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.db.database import Base

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
        Base.metadata.drop_all(bind=engine)


def test_process_platform_skips_unimplemented(db_session):
    job = IngestPlatformJob(platform="google", lookback_days=30)
    result = JobProcessor(db_session).process_platform(job)
    assert result["status"] == "skipped"
    assert result["campaigns_processed"] == 0


@patch("app.worker.processor.create_poller")
def test_process_campaign_facebook(mock_create_poller, db_session):
    poller = MagicMock()
    poller.fetch_campaign.return_value = []
    mock_create_poller.return_value = poller

    job = IngestCampaignJob(
        platform="facebook",
        campaign_id="fb_camp_123",
        since=date(2026, 4, 1),
        until=date(2026, 4, 2),
    )
    result = JobProcessor(db_session).process_campaign(job)

    assert result["status"] == "ok"
    assert result["fetched"] == 0
    poller.fetch_campaign.assert_called_once_with(
        "fb_camp_123", date(2026, 4, 1), date(2026, 4, 2)
    )
    poller.close.assert_called_once()
