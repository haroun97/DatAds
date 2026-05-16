"""
Google Ads poller (Platform B).

Endpoint: GET /api/reports/campaigns
Auth: Authorization: Bearer {GOOGLE_TOKEN}
Pagination: page_token from nextPageToken
Field mapping:
  campaignId -> campaign_id
  adId -> ad_id
  metrics.cost -> spend
  metrics.conversionValue -> revenue
"""

from datetime import date

from app.pollers.base import BasePoller
from app.schemas.ad_performance import AdPerformanceCreate


class GooglePoller(BasePoller):
    """Stub for extensibility — implement using the same pattern as FacebookPoller."""

    platform = "google"

    def fetch(self, since: date, until: date, **kwargs) -> list[AdPerformanceCreate]:
        raise NotImplementedError(
            "Google poller is scaffolded for extensibility. See module docstring."
        )
