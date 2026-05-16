from datetime import date

from pydantic import BaseModel

from app.schemas.ad_performance import AdPerformanceRecord


class AggregatedPerformance(BaseModel):
    total_impressions: int
    total_clicks: int
    total_spend: float
    total_revenue: float
    average_ctr: float
    average_cpc: float
    average_roas: float


class PerformanceResponse(BaseModel):
    data: AggregatedPerformance
    filters_applied: dict[str, str | None]


class TopPerformingResponse(BaseModel):
    data: list[AdPerformanceRecord]
    pagination: dict[str, int]
