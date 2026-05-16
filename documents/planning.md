# DatAds Take-Home — Project Planning & Status

**Last updated:** 2026-05-16  
**Stack:** Python 3.12 · FastAPI · SQLAlchemy · PostgreSQL / SQLite · httpx · tenacity · pytest

---

## Executive Summary

The core pipeline is **working end-to-end**: Facebook data is ingested from the mock API, stored with deduplication, metrics are calculated, and the REST API returns aggregated results (verified in browser at `/api/performance`).

**Overall progress:** ~85% of required scope · ~70% including optional/bonus items

| Part | Required? | Status |
|------|-----------|--------|
| Part 1 — System Design | Yes | Done |
| Part 2 — Polling & Processing | Yes | Done (Facebook); Google/TikTok stubbed |
| Part 3 — Query API | Bonus | Done |
| Part 4 — Submission | Yes | Not started |
| Tests | Bonus | Done (13 passing) |
| Deployment | Bonus | Not started |

---

## What’s Done

### Part 1 — System Design

| Item | Status | Location |
|------|--------|----------|
| Architecture diagram | Done | `part_1/system_design.png` |
| Written explanation (reliability, scalability, failures) | Done | `part_1/README.md` |
| Production-scale design notes | Done | `part_1/README.md`, `documents/datads_delivery_plan.md` |

### Part 2 — Data Polling & Processing

| Item | Status | Location |
|------|--------|----------|
| Facebook poller (cursor pagination) | Done | `app/pollers/facebook.py` |
| Retry + exponential backoff (429, 5xx, network) | Done | `app/utils/retry.py` |
| Normalization to common schema | Done | `app/pollers/facebook.py` |
| CTR / CPC / ROAS calculation | Done | `app/services/metrics_service.py` |
| Zero-division guards | Done | `app/services/metrics_service.py` |
| Persistent storage | Done | `app/db/models.py`, `app/db/repositories.py` |
| Deduplication (unique constraint + upsert) | Done | DB constraint + `ON CONFLICT` |
| Last 30 days ingestion script | Done | `scripts/ingest_facebook.py` |
| Error handling & logging | Done | pollers, services, `app/core/logging.py` |
| Alembic migration | Done | `alembic/versions/001_create_ad_performance.py` |
| Docker Compose (Postgres on port 5433) | Done | `docker-compose.yml` |
| SQLite fallback (no Docker) | Done | `scripts/dev.sh`, `.env` |
| Part 2 documentation | Done | `part_2/README.md` |
| Google poller stub + field mapping docs | Done (stub) | `app/pollers/google.py` |
| TikTok poller stub + field mapping docs | Done (stub) | `app/pollers/tiktok.py` |

**Verified locally:**
- Ingestion: 87 Facebook records per run (3 campaigns × ~29 days)
- API: `/api/performance?platform=facebook&date_from=2026-04-17&date_to=2026-05-16` returns valid aggregates

### Part 3 — Query API (Bonus)

| Item | Status | Location |
|------|--------|----------|
| `GET /api/performance` | Done | `app/api/routes.py` |
| `GET /api/top-performing` | Done | `app/api/routes.py` |
| Filters: platform, date_from, date_to, campaign_id | Done | `app/services/analytics_service.py` |
| Input validation (metric, order, limit, dates) | Done | `app/api/routes.py` |
| Aggregate CTR/CPC/ROAS from totals | Done | `app/services/analytics_service.py` |
| FastAPI auto-docs (`/docs`) | Done | `app/main.py` |
| Root redirect `/` → `/docs` | Done | `app/main.py` |
| Health endpoint | Done | `GET /health` |
| Part 3 documentation + curl examples | Done | `part_3/README.md` |

### Infrastructure & Quality

| Item | Status | Location |
|------|--------|----------|
| Project README (setup, troubleshooting) | Done | `README.md` |
| `requirements.txt` | Done | root |
| `.env.example` | Done | root |
| Unit & integration tests (13) | Done | `tests/` |
| Dev helper scripts | Done | `scripts/dev.sh`, `scripts/setup_postgres.sh` |

### Test Coverage

```
tests/test_metrics.py          — CTR, CPC, ROAS (incl. zero edge cases)
tests/test_deduplication.py    — unique constraint / upsert
tests/test_facebook_poller.py  — pagination, retry on 500
tests/test_api.py              — validation, performance, top-performing
```

Run: `pytest` → **13 passed**

---

## What’s Remaining

### Required for Submission (Part 4)

| Task | Priority | Notes |
|------|----------|-------|
| Initialize git repository | High | `git init`, `.gitignore` already exists |
| Push to **public** GitHub repo | High | Required deliverable |
| Submission email to daniel@datads.io | High | Include name, role, repo URL |
| Confirm folder structure matches spec | Medium | Code lives in `app/`; README explains mapping to `part_2/` / `part_3/` |

Suggested email checklist:
- [ ] Repository is public
- [ ] All parts present (part_1, part_2, part_3, README)
- [ ] No secrets in repo (`.env` gitignored)
- [ ] Sent ≥ 24 hours before interview

### Optional / Nice-to-Have (Before Interview)

| Task | Priority | Effort | Notes |
|------|----------|--------|-------|
| Implement Google poller | Medium | ~2–3 h | Stub exists; copy Facebook pattern |
| Implement TikTok poller | Medium | ~2–3 h | Offset pagination; stub exists |
| `scripts/ingest_all.py` | Low | ~30 min | Loop all platforms |
| Proactive rate-limit throttling | Low | ~1 h | Parse `/rate-limits`; sleep between requests |
| Job scheduler (cron / Celery Beat) | Low | Doc only OK | Task says on-demand is fine; discuss in interview |
| Deploy to Render / Railway | Medium | ~1–2 h | Bonus; add URL to README |
| PostgreSQL path smoke test | Medium | ~15 min | `docker-compose up -d` + port 5433 + migrate |
| Capture sample API output in `part_2/README` | Low | ~10 min | Screenshot or JSON snippet from live run |
| Add `campaign_id` filter to `/api/top-performing` | Low | ~15 min | Not in spec; skip unless needed |

### Known Gaps / Discuss in Interview

| Topic | Current State | Planned Answer |
|-------|---------------|----------------|
| Job scheduling | Manual script only | Cron → queue → workers in production |
| Google / TikTok | Stubs with mapping docs | Same poller interface; 1–2 days each |
| Rate limits | Reactive (retry on 429) | Proactive token bucket per platform |
| Scale (1000s RPS) | Single-process API | Cache, read replicas, pre-aggregated tables |
| Raw data retention | Not stored | S3 / JSONB for audit and reprocessing |

---

## Recommended Next Steps (Ordered)

### This week — submission blockers

1. **Git + GitHub** (~30 min)
   ```bash
   git init
   git add .
   git commit -m "DatAds take-home: Parts 1–3"
   # Create public repo on GitHub, push
   ```

2. **Final README pass** (~20 min)
   - Add your name at the top
   - Paste one real `/api/performance` JSON response
   - Note AI usage (already in README)

3. **Send submission email** (~5 min)

### If time allows before interview

4. **Google poller** — highest value for “extensibility” question  
5. **Deploy API** — strong bonus signal (Render free tier + Postgres)  
6. **PostgreSQL verification** — run `scripts/setup_postgres.sh` once

---

## Local Run Reference

### Quick (SQLite — current setup)

```bash
source venv/bin/activate
./scripts/dev.sh
# → http://127.0.0.1:8000/docs
```

### PostgreSQL (Docker)

```bash
docker-compose up -d
# .env: DATABASE_URL=postgresql+psycopg://datads:datads@localhost:5433/datads
alembic upgrade head
python scripts/ingest_facebook.py
uvicorn app.main:app --reload
```

### Key URLs

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/docs | Interactive API docs |
| http://127.0.0.1:8000/api/performance?platform=facebook | Aggregated metrics |
| http://127.0.0.1:8000/api/top-performing?metric=roas&limit=5 | Top ads |

---

## Submission Folder Mapping

The assignment asks for code under `part_2/` and `part_3/`. This repo uses a unified `app/` package (cleaner for a real project). Mapping:

| Assignment path | Actual location |
|-----------------|-----------------|
| `part_2/*.py` | `app/pollers/`, `app/services/`, `app/db/`, `scripts/` |
| `part_3/*.py` | `app/api/`, `app/main.py` |
| `part_2/README.md` | `part_2/README.md` |
| `part_3/README.md` | `part_3/README.md` |
| `requirements.txt` | root `requirements.txt` |

No action required unless the reviewer insists on duplicated files — the root README already explains this.

---

## Progress Checklist (from delivery plan)

### Part 1
- [x] system_design.png
- [x] part_1/README.md
- [x] Architecture, scalability, reliability explanations

### Part 2
- [x] Facebook poller
- [x] Pagination
- [x] Retry logic
- [x] Persistence (Postgres + SQLite)
- [x] Deduplication
- [x] Metrics calculation
- [x] Ingestion script
- [x] Sample output (verified live)
- [x] part_2/README.md
- [ ] Google poller (stub only)
- [ ] TikTok poller (stub only)

### Part 3 (Bonus)
- [x] FastAPI app
- [x] GET /api/performance
- [x] GET /api/top-performing
- [x] Input validation
- [x] part_3/README.md
- [ ] Deployment URL

### Testing
- [x] Metric tests
- [x] Deduplication tests
- [x] Poller pagination tests
- [x] Retry tests
- [x] API validation tests

### Final submission
- [ ] Public GitHub repository
- [ ] Submission email
- [x] README complete
- [x] requirements.txt
- [x] docker-compose.yml
- [x] Tests included

---

## Reference Documents

| Document | Purpose |
|----------|---------|
| `documents/dataAds_task.md` | Official assignment spec |
| `documents/datads_delivery_plan.md` | Full implementation plan & interview talking points |
| `documents/planning.md` | This file — status tracker |
