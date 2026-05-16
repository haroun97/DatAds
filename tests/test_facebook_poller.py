from datetime import date

import httpx

from app.core.config import get_settings
from app.pollers.facebook import FacebookPoller

settings = get_settings()


def _make_poller(handler) -> FacebookPoller:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(
        base_url=settings.api_base_url,
        transport=transport,
        headers={"x-api-key": settings.facebook_api_key},
    )
    return FacebookPoller(client=client)


def test_facebook_poller_pagination():
    campaign = "fb_camp_123"

    def handler(request: httpx.Request) -> httpx.Response:
        assert f"/api/v1/campaigns/{campaign}/insights" in str(request.url)
        if "after" not in request.url.params:
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "campaign_id": campaign,
                            "ad_id": "fb_ad_1",
                            "date": "2026-04-16",
                            "impressions": 100,
                            "clicks": 10,
                            "spend": 5.0,
                            "conversions": 1,
                            "revenue": 20.0,
                        }
                    ],
                    "paging": {"next": "1"},
                },
            )
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "campaign_id": campaign,
                        "ad_id": "fb_ad_2",
                        "date": "2026-04-17",
                        "impressions": 200,
                        "clicks": 20,
                        "spend": 10.0,
                        "conversions": 2,
                        "revenue": 40.0,
                    }
                ],
                "paging": {},
            },
        )

    poller = _make_poller(handler)
    records = poller.fetch_campaign(
        campaign, date(2026, 4, 16), date(2026, 4, 20), limit=100
    )
    poller.close()

    assert len(records) == 2
    assert records[0].ad_id == "fb_ad_1"
    assert records[1].ad_id == "fb_ad_2"
    assert records[0].ctr == 0.1


def test_facebook_poller_retries_on_500():
    campaign = "fb_camp_123"
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(500, json={"error": "server error"})
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "campaign_id": campaign,
                        "ad_id": "fb_ad_1",
                        "date": "2026-04-16",
                        "impressions": 100,
                        "clicks": 10,
                        "spend": 5.0,
                        "conversions": 1,
                        "revenue": 20.0,
                    }
                ],
                "paging": {},
            },
        )

    poller = _make_poller(handler)
    records = poller.fetch_campaign(
        campaign, date(2026, 4, 16), date(2026, 4, 16), limit=100
    )
    poller.close()

    assert len(records) == 1
    assert calls["count"] == 2
