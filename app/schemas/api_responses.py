# Pydantic models that define the shape of JSON responses returned by the API.

from datetime import date

from pydantic import BaseModel

from app.schemas.ad_performance import AdPerformanceRecord


class AggregatedPerformance(BaseModel):
    # Totals and averages across all ads that matched the request filters.
    total_impressions: int
    total_clicks: int
    total_spend: float
    total_revenue: float
    average_ctr: float
    average_cpc: float
    average_roas: float


class PerformanceResponse(BaseModel):
    # Wraps AggregatedPerformance with the filters that were applied to produce it.
    data: AggregatedPerformance
    filters_applied: dict[str, str | None]


class TopPerformingResponse(BaseModel):
    # `data` contains the requested page of ads; `pagination` carries total count.
    data: list[AdPerformanceRecord]
    pagination: dict[str, int]
