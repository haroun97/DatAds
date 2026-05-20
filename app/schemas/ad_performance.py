# Pydantic schemas for ad performance data.
# AdPerformanceCreate is used when writing to the DB; AdPerformanceRecord is used when reading.

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AdPerformanceCreate(BaseModel):
    # Fields required to insert a new row — all metric columns default to 0
    # so partial data from an API can still be stored without errors.
    platform: str
    campaign_id: str
    ad_id: str
    date: date
    impressions: int = 0
    clicks: int = 0
    spend: float = 0
    conversions: int = 0
    revenue: float = 0
    ctr: float = 0
    cpc: float = 0
    roas: float = 0


class AdPerformanceRecord(BaseModel):
    # Read model — from_attributes=True lets Pydantic read fields directly from ORM rows.
    model_config = ConfigDict(from_attributes=True)

    ad_id: str
    campaign_id: str
    platform: str
    date: date
    impressions: int
    clicks: int
    spend: float
    revenue: float
    ctr: float
    cpc: float
    roas: float


class PerformanceFilters(BaseModel):
    # All filters are optional — None means "don't filter on this field".
    platform: str | None = None
    campaign_id: str | None = None
    date_from: date | None = None
    date_to: date | None = None


# Type aliases used as parameter/return type hints in routes and services.
MetricName = Literal["ctr", "cpc", "roas", "clicks", "revenue"]
SortOrder = Literal["asc", "desc"]
