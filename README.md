# DatAds Take-Home Solution

**Author:** Haroun Louati

Backend system that ingests ad performance data from mock ad platform APIs, normalizes and stores it, calculates CTR/CPC/ROAS, and exposes aggregated insights via a REST API.

## Live deployment

| Resource | URL |
|----------|-----|
| API docs | https://datads.onrender.com/docs |
| Health | https://datads.onrender.com/health |
| Repository | https://github.com/haroun97/DatAds |

Example calls (production):

```bash
curl "https://datads.onrender.com/api/performance?platform=facebook&date_from=2026-04-19&date_to=2026-05-18"
curl "https://datads.onrender.com/api/top-performing?metric=roas&limit=5&platform=facebook&date_from=2026-04-19&date_to=2026-05-18"
```

## Architecture

```text
EventBridge Scheduler → SQS Queue → ECS Fargate Workers → Platform Pollers
        → Normalization → Deduplication → PostgreSQL → Aggregation → REST API
```

See [part_1/README.md](part_1/README.md) for the full system design and [part_1/system_design.png](part_1/system_design.png) for the architecture diagram.

The working implementation lives in `app/` (Parts 2 and 3). Task-specific documentation is in `part_1/`, `part_2/`, and `part_3/`.

## Tech Stack

| Area | Technology |
|------|------------|
| Language | Python 3.12 |
| API | FastAPI + uvicorn |
| HTTP client | httpx |
| Database | PostgreSQL (SQLite supported for quick local runs) |
| ORM | SQLAlchemy + Alembic |
| Retries | tenacity |
| Tests | pytest |

## Quick Start

### Option A — SQLite (no Docker, fastest)

```bash
source venv/bin/activate   # create venv first if needed: python3 -m venv venv && pip install -r requirements.txt
chmod +x scripts/dev.sh
./scripts/dev.sh
```

Or manually:

```bash
export DATABASE_URL=sqlite:///./datads.db
alembic upgrade head
python3 scripts/ingest_facebook.py
uvicorn app.main:app --reload
```

### Option B — PostgreSQL via Docker

> Use `docker-compose` (not `docker compose`) if you see `unknown shorthand flag: 'd'`.
> Docker maps Postgres to **port 5433** so it does not clash with a system Postgres on 5432.

```bash
docker-compose up -d
cp .env.example .env   # DATABASE_URL uses port 5433
source venv/bin/activate
alembic upgrade head
python3 scripts/ingest_facebook.py
uvicorn app.main:app --reload
```

Or run the helper script:

```bash
chmod +x scripts/setup_postgres.sh
./scripts/setup_postgres.sh
```

Open interactive docs: http://localhost:8000/docs

### 6. Example API calls

```bash
# Aggregated performance
curl "http://localhost:8000/api/performance?platform=facebook&date_from=2026-04-17&date_to=2026-05-16"

# Top ads by ROAS
curl "http://localhost:8000/api/top-performing?metric=roas&limit=5&platform=facebook"
```

### 7. Run tests

```bash
pytest
```

## Deploy on Render

1. Push repo to GitHub and connect on [Render](https://render.com).
2. Create a **PostgreSQL** database; link `DATABASE_URL` to the web service.
3. **Start command:**
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Or use the included `render.yaml` blueprint (Web Service + Postgres).

Render sets `DATABASE_URL` as `postgres://...`. The app rewrites that to `postgresql+psycopg://...` so it uses **psycopg v3** (in `requirements.txt`), not `psycopg2`.

After deploy, ingest data once (Render Shell or locally against prod DB):

```bash
python3 scripts/ingest_facebook.py
```

API will return empty aggregates until data is ingested.

## Troubleshooting

| Error | Cause | Fix |
|-------|--------|-----|
| `No module named 'psycopg2'` on Render | `DATABASE_URL` is `postgres://` without driver | Fixed in `app/core/config.py` — redeploy latest code |
| `unknown shorthand flag: 'd'` | Old Docker CLI | Use `docker-compose up -d` instead of `docker compose up -d` |
| `password authentication failed for user "datads"` | Port 5432 is your **system** Postgres, not Docker | Use Option A (SQLite) or Docker on port **5433** (see `.env.example`) |
| `Address already in use` (port 8000) | API already running | `pkill -f "uvicorn app.main"` or use another port: `--port 8001` |

## AWS scheduled ingestion

Production-style pipeline: **EventBridge Scheduler → SQS → ECS workers**.

See [infrastructure/README.md](infrastructure/README.md) for deploy steps, job JSON contract, and operations.

```bash
cd infrastructure/terraform && terraform apply
./scripts/deploy_worker_aws.sh
```

## Production Improvements

- Raw API response storage (S3 / JSONB) for audit and reprocessing
- Redis cache for hot query paths
- Read replicas and pre-aggregated tables for high QPS
- Full Google and TikTok poller implementations (stubs included)

## AI Usage

I used AI tools (Claude) as a coding assistant for debugging, boilerplate, and documentation review. The system design, architecture decisions (SQS fan-out, ECS workers, deduplication strategy, metric aggregation), and implementation were designed and validated by me. I used AI as a tool for iteration and feedback, but I made the final engineering decisions.
