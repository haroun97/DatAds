from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AdPerformanceCreate(BaseModel):
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
    platform: str | None = None
    campaign_id: str | None = None
    date_from: date | None = None
    date_to: date | None = None


MetricName = Literal["ctr", "cpc", "roas", "clicks", "revenue"]
SortOrder = Literal["asc", "desc"]
