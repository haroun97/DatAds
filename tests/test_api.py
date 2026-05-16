from datetime import date

from app.db.repositories import AdPerformanceRepository
from app.schemas.ad_performance import AdPerformanceCreate
from app.services.metrics_service import enrich_metrics


def _seed_record(db_session, ad_id: str, roas: float = 5.0):
    metrics = enrich_metrics(impressions=1000, clicks=100, spend=50.0, revenue=50.0 * roas)
    metrics["roas"] = roas
    record = AdPerformanceCreate(
        platform="facebook",
        campaign_id="fb_camp_123",
        ad_id=ad_id,
        date=date(2026, 5, 1),
        impressions=1000,
        clicks=100,
        spend=50.0,
        conversions=10,
        revenue=50.0 * roas,
        **metrics,
    )
    AdPerformanceRepository(db_session).upsert_many([record])


def test_invalid_metric_returns_400(client):
    response = client.get("/api/top-performing?metric=invalid")
    assert response.status_code == 400
    assert "Invalid metric" in response.json()["detail"]


def test_limit_over_100_returns_422(client):
    response = client.get("/api/top-performing?metric=roas&limit=101")
    assert response.status_code == 422


def test_performance_empty(client):
    response = client.get("/api/performance?platform=facebook")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total_impressions"] == 0
    assert body["filters_applied"]["platform"] == "facebook"


def test_top_performing_sorted(client, db_session):
    _seed_record(db_session, "fb_ad_low", roas=2.0)
    _seed_record(db_session, "fb_ad_high", roas=10.0)

    response = client.get("/api/top-performing?metric=roas&limit=1&platform=facebook")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["ad_id"] == "fb_ad_high"
    assert body["pagination"]["total"] == 2
