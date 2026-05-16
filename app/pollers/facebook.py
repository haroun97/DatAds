import logging
from datetime import date

import httpx

from app.core.config import get_settings
from app.pollers.base import BasePoller
from app.schemas.ad_performance import AdPerformanceCreate
from app.services.metrics_service import enrich_metrics
from app.utils.retry import api_retry, raise_for_retryable_response

logger = logging.getLogger(__name__)

FACEBOOK_CAMPAIGNS = ["fb_camp_123", "fb_camp_456", "fb_camp_789"]


class FacebookPoller(BasePoller):
    platform = "facebook"

    def __init__(self, client: httpx.Client | None = None):
        self.settings = get_settings()
        self._client = client
        self._owns_client = client is None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.settings.api_base_url,
                timeout=self.settings.http_timeout_seconds,
                headers={"x-api-key": self.settings.facebook_api_key},
            )
        return self._client

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    def fetch_campaign(
        self, campaign_id: str, since: date, until: date, limit: int = 100
    ) -> list[AdPerformanceCreate]:
        records: list[AdPerformanceCreate] = []
        cursor: str | None = None

        while True:
            page = self._fetch_page(campaign_id, since, until, limit, cursor)
            records.extend(page["records"])
            cursor = page.get("next_cursor")
            if not cursor:
                break

        logger.info(
            "Fetched %d Facebook records for campaign %s (%s to %s)",
            len(records),
            campaign_id,
            since,
            until,
        )
        return records

    def fetch(self, since: date, until: date, **kwargs) -> list[AdPerformanceCreate]:
        campaign_ids = kwargs.get("campaign_ids", FACEBOOK_CAMPAIGNS)
        all_records: list[AdPerformanceCreate] = []
        for campaign_id in campaign_ids:
            all_records.extend(self.fetch_campaign(campaign_id, since, until))
        return all_records

    @api_retry()
    def _fetch_page(
        self,
        campaign_id: str,
        since: date,
        until: date,
        limit: int,
        cursor: str | None,
    ) -> dict:
        client = self._get_client()
        params: dict[str, str | int] = {
            "since": since.isoformat(),
            "until": until.isoformat(),
            "limit": limit,
        }
        if cursor:
            params["after"] = cursor

        url = f"/api/v1/campaigns/{campaign_id}/insights"
        response = client.get(url, params=params)
        raise_for_retryable_response(response)
        payload = response.json()

        records = [self._normalize(item) for item in payload.get("data", [])]
        paging = payload.get("paging") or {}
        next_cursor = paging.get("next")

        return {"records": records, "next_cursor": next_cursor}

    def _normalize(self, item: dict) -> AdPerformanceCreate:
        impressions = int(item.get("impressions", 0))
        clicks = int(item.get("clicks", 0))
        spend = float(item.get("spend", 0))
        revenue = float(item.get("revenue", 0))
        metrics = enrich_metrics(
            impressions=impressions,
            clicks=clicks,
            spend=spend,
            revenue=revenue,
        )
        return AdPerformanceCreate(
            platform=self.platform,
            campaign_id=item["campaign_id"],
            ad_id=item["ad_id"],
            date=date.fromisoformat(item["date"]),
            impressions=impressions,
            clicks=clicks,
            spend=spend,
            conversions=int(item.get("conversions", 0)),
            revenue=revenue,
            **metrics,
        )
