import logging
from datetime import date

from sqlalchemy.orm import Session

from app.db.repositories import AdPerformanceRepository
from app.pollers.base import BasePoller
from app.schemas.ingest_job import IngestCampaignJob, IngestPlatformJob
from app.utils.dates import last_n_days
from app.worker.registry import IMPLEMENTED_PLATFORMS, campaign_ids_for, create_poller

logger = logging.getLogger(__name__)


class JobProcessor:
    def __init__(self, db: Session):
        self.repo = AdPerformanceRepository(db)

    def process_platform(self, job: IngestPlatformJob) -> dict[str, int | str]:
        if job.platform not in IMPLEMENTED_PLATFORMS:
            logger.warning(
                "Skipping platform %s (poller not implemented); job_id=%s",
                job.platform,
                job.job_id,
            )
            return {
                "job_id": str(job.job_id),
                "platform": job.platform,
                "campaigns_processed": 0,
                "status": "skipped",
            }

        since, until = last_n_days(job.lookback_days)
        campaign_ids = campaign_ids_for(job.platform)
        if not campaign_ids:
            logger.warning("No campaigns configured for platform %s", job.platform)
            return {
                "job_id": str(job.job_id),
                "platform": job.platform,
                "campaigns_processed": 0,
                "status": "no_campaigns",
            }

        poller = create_poller(job.platform)
        totals = {"fetched": 0, "inserted": 0, "updated": 0, "campaigns_processed": 0}
        try:
            for campaign_id in campaign_ids:
                summary = self._ingest_campaign(
                    poller=poller,
                    platform=job.platform,
                    campaign_id=campaign_id,
                    since=since,
                    until=until,
                )
                totals["fetched"] += summary["fetched"]
                totals["inserted"] += summary["inserted"]
                totals["updated"] += summary["updated"]
                totals["campaigns_processed"] += 1
        finally:
            if hasattr(poller, "close"):
                poller.close()

        logger.info(
            "Platform ingest complete: platform=%s job_id=%s summary=%s",
            job.platform,
            job.job_id,
            totals,
        )
        return {"job_id": str(job.job_id), "platform": job.platform, **totals, "status": "ok"}

    def process_campaign(self, job: IngestCampaignJob) -> dict[str, int | str]:
        if job.platform not in IMPLEMENTED_PLATFORMS:
            logger.warning(
                "Skipping campaign job for unimplemented platform %s; job_id=%s",
                job.platform,
                job.job_id,
            )
            return {
                "job_id": str(job.job_id),
                "platform": job.platform,
                "campaign_id": job.campaign_id,
                "status": "skipped",
            }

        poller = create_poller(job.platform)
        try:
            summary = self._ingest_campaign(
                poller=poller,
                platform=job.platform,
                campaign_id=job.campaign_id,
                since=job.since,
                until=job.until,
            )
        finally:
            if hasattr(poller, "close"):
                poller.close()

        logger.info(
            "Campaign ingest complete: platform=%s campaign=%s job_id=%s summary=%s",
            job.platform,
            job.campaign_id,
            job.job_id,
            summary,
        )
        return {
            "job_id": str(job.job_id),
            "platform": job.platform,
            "campaign_id": job.campaign_id,
            **summary,
            "status": "ok",
        }

    def _ingest_campaign(
        self,
        poller: BasePoller,
        platform: str,
        campaign_id: str,
        since: date,
        until: date,
    ) -> dict[str, int]:
        if platform == "facebook":
            records = poller.fetch_campaign(campaign_id, since, until)  # type: ignore[attr-defined]
        else:
            records = poller.fetch(since, until, campaign_ids=[campaign_id])

        inserted, updated = self.repo.upsert_many(records)
        summary = {"fetched": len(records), "inserted": inserted, "updated": updated}
        logger.info(
            "Ingested campaign %s (%s): %s",
            campaign_id,
            platform,
            summary,
        )
        return summary
