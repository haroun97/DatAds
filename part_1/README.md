# Part 1 — System Design

## Architecture Diagram

![Production Architecture](system_design_v2.png)

For local development you can also run ingestion with `scripts/ingest_facebook.py` (same pollers and database logic; no EventBridge or SQS). Production uses the flow below.

```text
EventBridge Scheduler (Facebook: 1h / Google: 2h / TikTok: 3h)
        ↓
SQS Ingest Queue  ──→  DLQ (after 3 failures)  ──→  CloudWatch Alarm → SNS
        ↓
ECS Fargate Workers (horizontally scalable, graceful SIGTERM shutdown)
        ↓
Platform Pollers (Facebook, Google, TikTok)  ←── Retry + Exponential Backoff
        ↓
Normalization Layer  (unified schema: platform, campaign_id, ad_id, date, …)
        ↓
Deduplication  (ON CONFLICT DO UPDATE on platform + campaign_id + ad_id + date)
        ↓
PostgreSQL  (unique constraint + indexes on platform, date, campaign, ctr, cpc, roas)
        ↓
Aggregation at Query Time  (CTR = clicks/impressions, CPC = spend/clicks, ROAS = revenue/spend)
        ↓
REST API — FastAPI  (GET /api/performance, GET /api/top-performing)
```

Infrastructure is implemented under `infrastructure/terraform/` and `app/worker/`.

---

## Architectural Choices

**Separation of ingestion and query paths.** External ad APIs are slow, rate-limited, and unreliable. The REST API reads only from the database, so user-facing queries stay fast and stable even when upstream APIs fail.

**Platform-specific pollers behind a common interface.** Each ad platform uses different endpoints, authentication, pagination, and field names. A `BasePoller` ABC isolates that complexity in dedicated classes (`FacebookPoller`, `GooglePoller`, `TikTokPoller`), keeping the rest of the system platform-agnostic. Adding a new platform is a single new class.

**Normalization before storage.** All platforms are mapped to one internal model (`platform`, `campaign_id`, `ad_id`, `date`, `impressions`, `clicks`, `spend`, `revenue`). This simplifies metric calculation, deduplication, and API filtering.

**PostgreSQL with a unique constraint** on `(platform, campaign_id, ad_id, date)` for idempotent ingestion. Re-fetching overlapping date ranges updates existing rows (`ON CONFLICT DO UPDATE`) instead of creating duplicates.

**Asynchronous job queue (SQS).** Decouples the scheduler from the workers. Workers can scale horizontally by adding ECS task replicas. SQS visibility timeout acts as a distributed lock — if a worker crashes mid-job, the message becomes visible again automatically.

**Dead Letter Queue (DLQ).** After 3 delivery failures, a message moves to the DLQ. A CloudWatch alarm fires an SNS notification so the on-call engineer is alerted without any polling.

---

## Reliability

| Failure | Strategy |
|---------|----------|
| 5xx from ad API | Exponential backoff retry (up to 4 attempts via `tenacity`) |
| 429 rate limit | Retry with backoff; page sizes kept below platform limits |
| Network timeout | Retry; `httpx` timeout configured (30 s) |
| Worker crash mid-job | SQS visibility timeout → message re-queued automatically |
| Persistent failures | DLQ after 3 attempts → CloudWatch alarm → SNS alert |
| Duplicate data | PostgreSQL `ON CONFLICT DO UPDATE` (idempotent upserts) |
| Invalid API input | FastAPI validation → 400/422 with clear messages |
| DLQ replay | `scripts/replay_dlq.py` for manual reprocessing |

---

## Scalability

### What scales well today

1. **Scheduler (EventBridge)** — Fires ingest jobs on a timer (e.g. Facebook every hour). You can add more platforms without changing worker code.
2. **Message queue (SQS)** — Jobs wait in the queue if workers are busy. Example: 100 jobs arrive at once; workers drain them over time instead of dropping work.
3. **Worker pool (ECS Fargate)** — Run more worker containers to process more jobs in parallel. Example: `desired_count = 5` means five workers pulling from SQS at once.
4. **Raw API responses (S3 or JSONB)** — Save the original JSON from Facebook/Google/TikTok so you can reprocess later without calling the APIs again.
5. **PostgreSQL + indexes** — Fine for the current size (3 platforms, a few campaigns, last 30 days). Queries filter by `platform` and `date` using indexes.
6. **Cache (Redis)** — *Planned, not wired yet.* Store answers like “Facebook totals for April” for a few minutes so repeated API calls do not hit the database every time.

The query API never calls external ad platforms — it only reads from our database. That keeps reads fast even when Facebook is slow or down.

### Known limits in the current code

| Limit | What happens now | Simple fix at larger scale |
|-------|------------------|----------------------------|
| **Totals in Python** | `/api/performance` loads all matching rows, then sums in code | Use SQL `SUM()` so the database does the math (e.g. one query for 1M rows) |
| **One campaign after another** | One `ingest_platform` job loops campaigns sequentially | Split into many `ingest_campaign` jobs on SQS so several workers run in parallel |
| **No cache** | Every API request runs a fresh DB query | Redis in front of `/api/performance` for common filters |
| **Platform rate limits** | Facebook ~200 req/hr; more workers do not help past that | Per-platform rate budget shared across workers |

### How the design fits different sizes

| Size | Fits? | Example | What to change |
|------|-------|---------|----------------|
| **Small** (this take-home) | Yes | 3 platforms, ~30 campaigns, 30 days of data | Nothing required |
| **Medium** | With tuning | 10 platforms, ~500 campaigns, steady API traffic | SQL aggregation, Redis cache, more ECS workers, fan-out campaign jobs |
| **Large** | Needs new pieces | Billions of rows, thousands of reads per second | ClickHouse or BigQuery for analytics, read replicas, pre-aggregated daily rollups |

To support very high read traffic (thousands of requests per second): read replicas, rollup tables (e.g. daily totals per platform), and Redis — still never calling external ad APIs from the query path.

---

## Metric Aggregation

For `/api/performance`, aggregate metrics are computed from totals, not averages of per-row rates:

```text
average_ctr  = total_clicks / total_impressions
average_cpc  = total_spend  / total_clicks
average_roas = total_revenue / total_spend
```

Averaging row-level CTR/CPC/ROAS values would be mathematically incorrect (different impression volumes per row get equal weight). Using totals gives the true weighted aggregate.
