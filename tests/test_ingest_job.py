# Tests for the SQS job payload parser in app/schemas/ingest_job.py.

from datetime import date

import pytest

from app.schemas.ingest_job import IngestCampaignJob, IngestPlatformJob, parse_ingest_job


def test_parse_platform_job():
    # A valid ingest_platform payload should deserialise into IngestPlatformJob.
    job = parse_ingest_job(
        {"job_type": "ingest_platform", "platform": "facebook", "lookback_days": 7}
    )
    assert isinstance(job, IngestPlatformJob)
    assert job.platform == "facebook"
    assert job.lookback_days == 7


def test_parse_campaign_job():
    # A valid ingest_campaign payload should deserialise into IngestCampaignJob with date objects.
    job = parse_ingest_job(
        {
            "job_type": "ingest_campaign",
            "platform": "facebook",
            "campaign_id": "fb_camp_123",
            "since": "2026-04-01",
            "until": "2026-04-30",
        }
    )
    assert isinstance(job, IngestCampaignJob)
    assert job.since == date(2026, 4, 1)
    assert job.until == date(2026, 4, 30)


def test_parse_unknown_job_type():
    # An unrecognised job_type should raise a ValueError, not silently return None.
    with pytest.raises(ValueError, match="Unknown job_type"):
        parse_ingest_job({"job_type": "unknown"})
