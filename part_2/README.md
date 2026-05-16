# Part 2 — Data Polling & Processing

Implementation files live in `app/pollers/`, `app/services/`, `app/db/`, and `scripts/ingest_facebook.py`.

## What Was Implemented

- **Facebook poller** with cursor-based pagination (`paging.next` → `after` param)
- **Retry logic** with exponential backoff for 429/5xx and network errors
- **Normalization** from Facebook API fields to the internal model
- **Metric calculation**: CTR, CPC, ROAS (with zero-division guards)
- **PostgreSQL persistence** via SQLAlchemy + Alembic migration
- **Deduplication** via unique constraint + upsert on conflict
- **Google/TikTok poller stubs** documenting field mappings for extensibility

## Run Ingestion

```bash
# Ensure DB is running and migrated
docker compose up -d
alembic upgrade head

# Ingest last 30 days of Facebook data
python scripts/ingest_facebook.py
```

## Sample Output

```text
Starting Facebook ingestion...
Date range: 2026-04-17 to 2026-05-16

Campaign fb_camp_123:
  Fetched 29 records
  Inserted 29 records
  Updated 0 records

Campaign fb_camp_456:
  Fetched 29 records
  Inserted 29 records
  Updated 0 records

Campaign fb_camp_789:
  Fetched 29 records
  Inserted 29 records
  Updated 0 records

Done.
Total fetched: 87
Total inserted: 87
Total updated: 0
```

Retry logic was exercised automatically when campaign `fb_camp_789` returned a simulated 500 error.

## Pagination

Facebook uses cursor pagination:

1. First request: `?since=...&until=...&limit=100`
2. If `paging.next` is present, follow with `?after={cursor}`
3. Stop when `paging.next` is absent

## Deduplication

Unique key: `(platform, campaign_id, ad_id, date)`

Re-ingesting the same data updates metrics in place via `ON CONFLICT DO UPDATE`.

## Metrics

| Metric | Formula |
|--------|---------|
| CTR | clicks / impressions |
| CPC | spend / clicks |
| ROAS | revenue / spend |

## Extensibility

To add Google or TikTok:

1. Implement `fetch()` in `app/pollers/google.py` or `tiktok.py`
2. Map platform-specific fields to `AdPerformanceCreate`
3. Reuse `IngestionService` and `AdPerformanceRepository`

## Tests

```bash
pytest tests/test_metrics.py tests/test_deduplication.py tests/test_facebook_poller.py
```
