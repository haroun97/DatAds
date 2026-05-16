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
        records: list[AdPerformanceCreate] = self.poller.fetch(since, until, **poller_kwargs)
        inserted, updated = self.repo.upsert_many(records)

        summary = {
            "fetched": len(records),
            "inserted": inserted,
            "updated": updated,
        }
        logger.info("Ingestion complete: %s", summary)
        return summary
