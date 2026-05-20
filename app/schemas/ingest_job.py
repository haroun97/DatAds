# Pydantic models for the SQS job payloads that trigger data ingestion.
# Two job types are supported:
#   - ingest_platform: ingest all known campaigns for a platform over a lookback window
#   - ingest_campaign: ingest a single campaign for a specific date range

from datetime import date
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class JobType(str, Enum):
    INGEST_PLATFORM = "ingest_platform"
    INGEST_CAMPAIGN = "ingest_campaign"


class IngestPlatformJob(BaseModel):
    # Sent by EventBridge on a schedule to refresh all campaigns for a platform.
    job_type: Literal[JobType.INGEST_PLATFORM] = JobType.INGEST_PLATFORM
    platform: str
    lookback_days: int = Field(default=30, ge=1, le=365)
    job_id: UUID = Field(default_factory=uuid4)   # auto-generated for tracing


class IngestCampaignJob(BaseModel):
    # Sent when a specific campaign/date-range needs to be (re-)ingested.
    job_type: Literal[JobType.INGEST_CAMPAIGN] = JobType.INGEST_CAMPAIGN
    platform: str
    campaign_id: str
    since: date
    until: date
    job_id: UUID = Field(default_factory=uuid4)


# Union type used in type hints — discriminated by the job_type field.
IngestJob = Annotated[IngestPlatformJob | IngestCampaignJob, Field(discriminator="job_type")]


def parse_ingest_job(payload: dict) -> IngestPlatformJob | IngestCampaignJob:
    # Parse a raw dict (e.g. from SQS message body) into the correct job model.
    # Supports both enum instances and plain string values for job_type.
    job_type = payload.get("job_type")
    if job_type in (JobType.INGEST_PLATFORM, JobType.INGEST_PLATFORM.value):
        return IngestPlatformJob.model_validate(payload)
    if job_type in (JobType.INGEST_CAMPAIGN, JobType.INGEST_CAMPAIGN.value):
        return IngestCampaignJob.model_validate(payload)
    raise ValueError(f"Unknown job_type: {job_type!r}")
