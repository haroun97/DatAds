# Part 2 — Data Polling & Processing

Implementation files live in the shared `app/` package (`app/pollers/`, `app/services/`, `app/db/`) and `scripts/ingest_facebook.py`, rather than `part_2/` directly, because the same code is used by both the manual script (Part 2) and the API server (Part 3).

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
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Start the database
docker-compose up -d

# 3. Run migrations
alembic upgrade head

# 4. Ingest last 30 days of Facebook data
python3 scripts/ingest_facebook.py
```

## Sample Output

```text
Starting Facebook ingestion...
Date range: 2026-04-17 to 2026-05-16

Campaign fb_camp_123:
  Fetched 29 records
  Inserted 29 records
  Updated 0 records
  Sample metrics — CTR: 0.0150, CPC: 0.5033, ROAS: 4.7682

Campaign fb_camp_456:
  Fetched 29 records
  Inserted 29 records
  Updated 0 records
  Sample metrics — CTR: 0.0120, CPC: 0.6250, ROAS: 3.9200

Campaign fb_camp_789:
  Fetched 29 records
  Inserted 29 records
  Updated 0 records
  Sample metrics — CTR: 0.0180, CPC: 0.4722, ROAS: 5.1340

Done.
Total fetched: 87
Total inserted: 87
Total updated: 0
```

Retry logic was exercised automatically when campaign `fb_camp_789` returned a simulated 500 error on one page request. The request was retried with exponential backoff (up to 4 attempts) and succeeded on the second attempt.

## Pagination

Facebook uses cursor pagination:

1. First request: `?since=...&until=...&limit=100`
2. If `paging.next` is present, follow with `?after={cursor}`
3. Stop when `paging.next` is absent

## Deduplication

Unique key: `(platform, campaign_id, ad_id, date)`

Re-ingesting the same data updates metrics in place via `ON CONFLICT DO UPDATE`.

**Mock API limitation:** The mock API returns a random `ad_id` on every call for the same
`(campaign_id, date)`, so running the ingestion script twice will insert new rows rather
than updating existing ones. In a real ad platform API (Facebook, Google, TikTok), `ad_id`
is a permanent identifier — stable across calls — so the upsert would correctly deduplicate.
The deduplication logic and schema are correct for production use; this is a quirk of the
mock only. The unit test in `tests/test_deduplication.py` validates the upsert behaviour
using a fixed `ad_id`, which reflects the real-world scenario.

## Metrics

| Metric | Formula | Zero case |
|--------|---------|-----------|
| CTR | clicks / impressions | 0.0 if impressions = 0 |
| CPC | spend / clicks | 0.0 if clicks = 0 |
| ROAS | revenue / spend | 0.0 if spend = 0 |

## Extensibility

To add Google or TikTok:

1. Implement `fetch()` in `app/pollers/google.py` or `tiktok.py`
2. Map platform-specific fields to `AdPerformanceCreate`
3. Reuse `IngestionService` and `AdPerformanceRepository`

## Tests

```bash
source venv/bin/activate
pytest tests/test_metrics.py tests/test_deduplication.py \
       tests/test_facebook_poller.py tests/test_ingest_job.py \
       tests/test_dates.py -v
```
