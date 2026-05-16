"""
TikTok Ads poller (Platform C).

Endpoint: GET /v1/ad/performance
Auth: Authorization: Bearer {TIKTOK_TOKEN}
Pagination: offset from response when has_more is true
Field mapping:
  campaign.id -> campaign_id
  campaign.ad_id -> ad_id
  performance.views -> impressions
  performance.engagements -> clicks
  performance.budget_spent -> spend
  performance.purchase_value -> revenue
"""

from datetime import date

from app.pollers.base import BasePoller
from app.schemas.ad_performance import AdPerformanceCreate


class TikTokPoller(BasePoller):
    """Stub for extensibility — implement using the same pattern as FacebookPoller."""

    platform = "tiktok"

    def fetch(self, since: date, until: date, **kwargs) -> list[AdPerformanceCreate]:
        raise NotImplementedError(
            "TikTok poller is scaffolded for extensibility. See module docstring."
        )
