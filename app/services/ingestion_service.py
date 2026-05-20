# Orchestrates a full ingestion run: poll the platform API then persist to the database.
# The service is intentionally thin — it delegates fetching to the poller and storage to the repo.

import logging
from datetime import date

from sqlalchemy.orm import Session

from app.db.repositories import AdPerformanceRepository
from app.pollers.base import BasePoller
from app.schemas.ad_performance import AdPerformanceCreate

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: Session, poller: BasePoller):
        self.repo = AdPerformanceRepository(db)
        self.poller = poller

    def ingest(self, since: date, until: date, **poller_kwargs) -> dict[str, int]:
        # Fetch all records from the platform for the given date window.
        records: list[AdPerformanceCreate] = self.poller.fetch(since, until, **poller_kwargs)
        # Upsert into the database — existing rows are updated, new ones are inserted.
        inserted, updated = self.repo.upsert_many(records)

        summary = {
            "fetched": len(records),
            "inserted": inserted,
            "updated": updated,
        }
        logger.info("Ingestion complete: %s", summary)
        return summary
