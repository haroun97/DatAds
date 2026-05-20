# Integration tests for the /api/performance and /api/top-performing endpoints.
# Uses the in-memory SQLite fixtures from conftest.py.

from datetime import date

from app.db.repositories import AdPerformanceRepository
from app.schemas.ad_performance import AdPerformanceCreate
from app.services.metrics_service import enrich_metrics


def _seed_record(db_session, ad_id: str, roas: float = 5.0):
    # Helper: insert a single ad record with a specific ROAS value for sorting tests.
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
    # Unknown metric names should be rejected before hitting the DB.
    response = client.get("/api/top-performing?metric=invalid")
    assert response.status_code == 400
    assert "Invalid metric" in response.json()["detail"]


def test_limit_over_100_returns_422(client):
    # FastAPI validates the limit range (1–100) automatically via Query(ge=1, le=100).
    response = client.get("/api/top-performing?metric=roas&limit=101")
    assert response.status_code == 422


def test_performance_empty(client):
    # With no data in the DB, all totals should be 0 and filters_applied should reflect the query.
    response = client.get("/api/performance?platform=facebook")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total_impressions"] == 0
    assert body["filters_applied"]["platform"] == "facebook"


def test_invalid_date_range_returns_400(client):
    # date_from after date_to is a user error — should get a 400, not a 500.
    response = client.get("/api/performance?date_from=2026-05-01&date_to=2026-04-01")
    assert response.status_code == 400
    assert "date_from" in response.json()["detail"]


def test_top_performing_sorted(client, db_session):
    # Seed two ads with different ROAS values and verify the higher one is returned first.
    _seed_record(db_session, "fb_ad_low", roas=2.0)
    _seed_record(db_session, "fb_ad_high", roas=10.0)

    response = client.get("/api/top-performing?metric=roas&limit=1&platform=facebook")
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["ad_id"] == "fb_ad_high"
    # pagination.total should be 2 even though only 1 row was returned.
    assert body["pagination"]["total"] == 2
