from datetime import date

from app.db.repositories import AdPerformanceRepository
from app.schemas.ad_performance import AdPerformanceCreate, PerformanceFilters
from app.services.metrics_service import enrich_metrics


def test_duplicate_record_upserts_once(db_session):
    metrics = enrich_metrics(impressions=1000, clicks=50, spend=25.0, revenue=100.0)
    record = AdPerformanceCreate(
        platform="facebook",
        campaign_id="fb_camp_123",
        ad_id="fb_ad_1",
        date=date(2026, 5, 1),
        impressions=1000,
        clicks=50,
        spend=25.0,
        conversions=5,
        revenue=100.0,
        **metrics,
    )
    repo = AdPerformanceRepository(db_session)
    repo.upsert_many([record])

    updated_metrics = enrich_metrics(impressions=2000, clicks=100, spend=50.0, revenue=200.0)
    duplicate = record.model_copy(
        update={"impressions": 2000, "clicks": 100, "spend": 50.0, "revenue": 200.0, **updated_metrics}
    )
    repo.upsert_many([duplicate])

    rows = repo.query_filtered(PerformanceFilters(platform="facebook"))
    assert len(rows) == 1
    assert rows[0].impressions == 2000
