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
        sort_key = {
            "ctr": lambda r: float(r.ctr),
            "cpc": lambda r: float(r.cpc),
            "roas": lambda r: float(r.roas),
            "clicks": lambda r: r.clicks,
            "revenue": lambda r: float(r.revenue),
        }[metric]

        reverse = order == "desc"
        sorted_rows = sorted(rows, key=sort_key, reverse=reverse)
        total = len(sorted_rows)
        page = sorted_rows[:limit]

        return [self._to_record(r) for r in page], total

    @staticmethod
    def _to_record(row: AdPerformance) -> AdPerformanceRecord:
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
