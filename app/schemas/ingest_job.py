from datetime import date
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class JobType(str, Enum):
    INGEST_PLATFORM = "ingest_platform"
    INGEST_CAMPAIGN = "ingest_campaign"


class IngestPlatformJob(BaseModel):
    job_type: Literal[JobType.INGEST_PLATFORM] = JobType.INGEST_PLATFORM
    platform: str
    lookback_days: int = Field(default=30, ge=1, le=365)
    job_id: UUID = Field(default_factory=uuid4)


class IngestCampaignJob(BaseModel):
    job_type: Literal[JobType.INGEST_CAMPAIGN] = JobType.INGEST_CAMPAIGN
    platform: str
    campaign_id: str
    since: date
    until: date
    job_id: UUID = Field(default_factory=uuid4)


IngestJob = Annotated[IngestPlatformJob | IngestCampaignJob, Field(discriminator="job_type")]


def parse_ingest_job(payload: dict) -> IngestPlatformJob | IngestCampaignJob:
    job_type = payload.get("job_type")
    if job_type in (JobType.INGEST_PLATFORM, JobType.INGEST_PLATFORM.value):
        return IngestPlatformJob.model_validate(payload)
    if job_type in (JobType.INGEST_CAMPAIGN, JobType.INGEST_CAMPAIGN.value):
        return IngestCampaignJob.model_validate(payload)
    raise ValueError(f"Unknown job_type: {job_type!r}")
