# Business logic for the analytics API endpoints.
# Reads from the database via the repository and applies aggregations / sorting in Python.

from sqlalchemy.orm import Session

from app.db.models import AdPerformance
from app.db.repositories import AdPerformanceRepository
from app.schemas.ad_performance import AdPerformanceRecord, MetricName, PerformanceFilters, SortOrder
from app.schemas.api_responses import AggregatedPerformance
from app.services.metrics_service import calculate_cpc, calculate_ctr, calculate_roas


class AnalyticsService:
    def __init__(self, db: Session):
        self.repo = AdPerformanceRepository(db)

    def get_aggregated_performance(self, filters: PerformanceFilters) -> AggregatedPerformance:
        # Pull all matching rows, then sum/average across them in Python.
        # This keeps the aggregation logic simple and testable without raw SQL.
        rows = self.repo.query_filtered(filters)
        total_impressions = sum(r.impressions for r in rows)
        total_clicks = sum(r.clicks for r in rows)
        total_spend = float(sum(r.spend for r in rows))
        total_revenue = float(sum(r.revenue for r in rows))

        return AggregatedPerformance(
            total_impressions=total_impressions,
            total_clicks=total_clicks,
            total_spend=round(total_spend, 2),
            total_revenue=round(total_revenue, 2),
            # Recompute CTR/CPC/ROAS from the totals so they reflect the full dataset,
            # not an average of per-row values.
            average_ctr=round(calculate_ctr(total_clicks, total_impressions), 6),
            average_cpc=round(calculate_cpc(total_spend, total_clicks), 6),
            average_roas=round(calculate_roas(total_revenue, total_spend), 6),
        )

    def get_top_performing(
        self,
        filters: PerformanceFilters,
        metric: MetricName,
        order: SortOrder = "desc",
        limit: int = 10,
    ) -> tuple[list[AdPerformanceRecord], int]:
        rows = self.repo.query_filtered(filters)

        # Map each metric name to a sort key function for the in-memory sort.
        sort_key = {
            "ctr": lambda r: float(r.ctr),
            "cpc": lambda r: float(r.cpc),
            "roas": lambda r: float(r.roas),
            "clicks": lambda r: r.clicks,
            "revenue": lambda r: float(r.revenue),
        }[metric]

        reverse = order == "desc"
        sorted_rows = sorted(rows, key=sort_key, reverse=reverse)
        # `total` is the count of all matching rows — returned for pagination metadata.
        total = len(sorted_rows)
        # Return only the requested slice, but include total so the client knows there's more.
        page = sorted_rows[:limit]

        return [self._to_record(r) for r in page], total

    @staticmethod
    def _to_record(row: AdPerformance) -> AdPerformanceRecord:
        # Convert a SQLAlchemy ORM row to the Pydantic response schema.
        # Explicit float() casts are needed because Numeric columns come back as Decimal.
        return AdPerformanceRecord(
            ad_id=row.ad_id,
            campaign_id=row.campaign_id,
            platform=row.platform,
            date=row.date,
            impressions=row.impressions,
            clicks=row.clicks,
            spend=float(row.spend),
            revenue=float(row.revenue),
            ctr=float(row.ctr),
            cpc=float(row.cpc),
            roas=float(row.roas),
        )
