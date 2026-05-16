from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.db.models import AdPerformance
from app.schemas.ad_performance import AdPerformanceCreate, PerformanceFilters


class AdPerformanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_many(self, records: list[AdPerformanceCreate]) -> tuple[int, int]:
        """Insert records; duplicates update metrics. Returns (inserted, updated/skipped)."""
        if not records:
            return 0, 0

        inserted = 0
        updated = 0
        dialect = self.db.bind.dialect.name

        for record in records:
            values = record.model_dump()
            if dialect == "postgresql":
                stmt = pg_insert(AdPerformance).values(**values)
                stmt = stmt.on_conflict_do_update(
                    constraint="uq_ad_performance",
                    set_={
                        "impressions": stmt.excluded.impressions,
                        "clicks": stmt.excluded.clicks,
                        "spend": stmt.excluded.spend,
                        "conversions": stmt.excluded.conversions,
                        "revenue": stmt.excluded.revenue,
                        "ctr": stmt.excluded.ctr,
                        "cpc": stmt.excluded.cpc,
                        "roas": stmt.excluded.roas,
                    },
                ).returning(AdPerformance.id, AdPerformance.created_at, AdPerformance.updated_at)
                result = self.db.execute(stmt).first()
                if result and result.created_at == result.updated_at:
                    inserted += 1
                else:
                    updated += 1
            else:
                stmt = sqlite_insert(AdPerformance).values(**values)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["platform", "campaign_id", "ad_id", "date"],
                    set_={
                        "impressions": stmt.excluded.impressions,
                        "clicks": stmt.excluded.clicks,
                        "spend": stmt.excluded.spend,
                        "conversions": stmt.excluded.conversions,
                        "revenue": stmt.excluded.revenue,
                        "ctr": stmt.excluded.ctr,
                        "cpc": stmt.excluded.cpc,
                        "roas": stmt.excluded.roas,
                    },
                )
                self.db.execute(stmt)
                inserted += 1

        self.db.commit()
        return inserted, updated

    def query_filtered(self, filters: PerformanceFilters) -> list[AdPerformance]:
        stmt = select(AdPerformance)
        if filters.platform:
            stmt = stmt.where(AdPerformance.platform == filters.platform)
        if filters.campaign_id:
            stmt = stmt.where(AdPerformance.campaign_id == filters.campaign_id)
        if filters.date_from:
            stmt = stmt.where(AdPerformance.date >= filters.date_from)
        if filters.date_to:
            stmt = stmt.where(AdPerformance.date <= filters.date_to)
        return list(self.db.scalars(stmt).all())

    def count_filtered(self, filters: PerformanceFilters) -> int:
        stmt = select(func.count()).select_from(AdPerformance)
        if filters.platform:
            stmt = stmt.where(AdPerformance.platform == filters.platform)
        if filters.campaign_id:
            stmt = stmt.where(AdPerformance.campaign_id == filters.campaign_id)
        if filters.date_from:
            stmt = stmt.where(AdPerformance.date >= filters.date_from)
        if filters.date_to:
            stmt = stmt.where(AdPerformance.date <= filters.date_to)
        return self.db.scalar(stmt) or 0
