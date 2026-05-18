# DatAds Take-Home — Manual Verification Guide

Use this document to **test every requirement** from `dataAds_task.md` and `datads_delivery_plan.md` against your implementation.

**How to use:** Work top to bottom. For each item, run the command, compare to **Expected**, and mark **Pass / Fail / N/A**.

---

## Before You Start

### Prerequisites

```bash
cd ~/Documents/Projects/DatAds
source venv/bin/activate
```

### Fresh run (recommended for a clean test)

```bash
# Option A — SQLite (fastest)
export DATABASE_URL=sqlite:///./datads_verify.db
rm -f datads_verify.db

# Option B — PostgreSQL (matches submission story)
# docker-compose up -d
# export DATABASE_URL=postgresql+psycopg://datads:datads@localhost:5433/datads

alembic upgrade head
python scripts/ingest_facebook.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Keep the API running in one terminal; use a second terminal for `curl` commands below.

### Date range note

The mock API returns Facebook data for **recent dates** (around today minus 30 days). Your ingestion script uses `last_n_days(30)` automatically. Replace `DATE_FROM` / `DATE_TO` below with the dates printed by the ingestion script.

```bash
# After ingestion, note the printed range, e.g.:
# Date range: 2026-04-17 to 2026-05-16
export DATE_FROM=2026-04-17
export DATE_TO=2026-05-16
```

---

## Part 0 — Mock API (External Service)

Verify the upstream APIs work **before** testing your code.

| # | Requirement (task spec) | Command | Expected | Pass? |
|---|-------------------------|---------|----------|-------|
| 0.1 | Mock API reachable | `curl -s "$API_BASE/health" \| python3 -m json.tool` | `"status": "healthy"` | ☐ |
| 0.2 | Rate limits endpoint | `curl -s "$API_BASE/rate-limits" \| python3 -m json.tool` | JSON with platform limits | ☐ |
| 0.3 | Facebook auth works | See 0.3 command below | HTTP 200, `data` array | ☐ |

```bash
export API_BASE="https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io"

curl -s "$API_BASE/health" | python3 -m json.tool
curl -s "$API_BASE/rate-limits" | python3 -m json.tool

curl -s -H "x-api-key: facebook_test_key_123" \
  "$API_BASE/api/v1/campaigns/fb_camp_123/insights?since=$DATE_FROM&until=$DATE_TO&limit=5" \
  | python3 -m json.tool
```

**Pass criteria:** Health returns 200. Facebook returns records (not empty `data: []`). If empty, widen dates or use dates from a successful ingestion run.

---

## Part 1 — System Design *(Required)*

| # | Deliverable (task spec) | How to verify | Pass? |
|---|-------------------------|---------------|-------|
| 1.1 | Architecture diagram (png/jpg/pdf) | Open `part_1/system_design.png` — readable, shows ingestion → DB → API | ☐ |
| 1.2 | Written explanation (1–2 paragraphs min) | Read `part_1/README.md` — covers choices, reliability, scalability | ☐ |
| 1.3 | Design covers: load from external API | Diagram or README mentions pollers / mock API | ☐ |
| 1.4 | Design covers: CTR, CPC, ROAS | Diagram or README mentions metrics layer | ☐ |
| 1.5 | Design covers: query API | Diagram or README mentions REST API | ☐ |
| 1.6 | Reliability (retries, failures) | `part_1/README.md` failure table or retry section | ☐ |
| 1.7 | Scalability (1000s RPS, scale extraction) | `part_1/README.md` scalability section | ☐ |
| 1.8 | Job scheduling (design only — impl optional) | Documented as manual script / future cron | ☐ |

**Manual check — open files:**

```bash
xdg-open part_1/system_design.png   # or open in IDE
less part_1/README.md
```

**Interview prep:** Be ready to explain queue + workers vs current manual script (see `datads_delivery_plan.md` §6).

---

## Part 2 — Data Polling & Processing *(Required)*

### 2.1 Deliverables & structure

| # | Deliverable | How to verify | Pass? |
|---|-------------|---------------|-------|
| 2.1.1 | Python implementation files exist | `ls app/pollers/ app/services/ app/db/ scripts/` | ☐ |
| 2.1.2 | `part_2/README.md` with run instructions | `cat part_2/README.md` | ☐ |
| 2.1.3 | `requirements.txt` at repo root | `cat requirements.txt` | ☐ |
| 2.1.4 | Sample output (CTR, CPC, ROAS) | Ingestion logs + DB spot-check (§2.5) | ☐ |

### 2.2 Facebook platform — last 30 days

| # | Requirement | How to verify | Pass? |
|---|-------------|---------------|-------|
| 2.2.1 | One platform implemented (Facebook) | `app/pollers/facebook.py` — full `fetch_campaign` | ☐ |
| 2.2.2 | Last 30 days date range | Run ingestion; output shows ~30-day range | ☐ |
| 2.2.3 | All 3 campaign IDs | Logs show `fb_camp_123`, `456`, `789` | ☐ |
| 2.2.4 | Extensibility (Google/TikTok) | Stubs exist: `google.py`, `tiktok.py` with mapping docs | ☐ |

```bash
python scripts/ingest_facebook.py
```

**Expected output (approximate):**

```text
Starting Facebook ingestion...
Date range: YYYY-MM-DD to YYYY-MM-DD   # ~30 days

Campaign fb_camp_123:
  Fetched ~29 records
  Inserted N records
  ...

Done.
Total fetched: ~87
```

| Pass? |
|-------|
| ☐ |

### 2.3 Pagination

| # | Requirement | How to verify | Pass? |
|---|-------------|---------------|-------|
| 2.3.1 | Cursor pagination (`after` + `paging.next`) | Code: `app/pollers/facebook.py` loop until no `next` | ☐ |
| 2.3.2 | Automated test | `pytest tests/test_facebook_poller.py::test_facebook_poller_pagination -v` | ☐ |

```bash
pytest tests/test_facebook_poller.py::test_facebook_poller_pagination -v
```

**Expected:** `1 passed`

| Pass? |
|-------|
| ☐ |

**Optional manual pagination proof** (small page size forces multiple pages):

```bash
python3 -c "
from datetime import date
from app.pollers.facebook import FacebookPoller
p = FacebookPoller()
r = p.fetch_campaign('fb_camp_123', date(2026,4,17), date(2026,5,16), limit=5)
p.close()
print('records', len(r))
"
```

If `limit=5` returns more than 5 records total, pagination ran.

### 2.4 Retry & error handling

| # | Requirement | How to verify | Pass? |
|---|-------------|---------------|-------|
| 2.4.1 | Exponential backoff on 429/5xx | `app/utils/retry.py` + tenacity on `_fetch_page` | ☐ |
| 2.4.2 | Network timeout | `http_timeout_seconds` in `app/core/config.py` | ☐ |
| 2.4.3 | Logging on retry | Re-run ingestion; watch for `WARNING ... Retrying` on 500 | ☐ |
| 2.4.4 | Automated retry test | `pytest tests/test_facebook_poller.py::test_facebook_poller_retries_on_500 -v` | ☐ |

```bash
pytest tests/test_facebook_poller.py::test_facebook_poller_retries_on_500 -v
```

| Pass? |
|-------|
| ☐ |

### 2.5 Metrics (CTR, CPC, ROAS)

| # | Formula (task spec) | Code location | Pass? |
|---|---------------------|---------------|-------|
| 2.5.1 | `ctr = clicks / impressions` | `app/services/metrics_service.py` | ☐ |
| 2.5.2 | `cpc = spend / clicks` | same | ☐ |
| 2.5.3 | `roas = revenue / spend` | same | ☐ |
| 2.5.4 | Zero-division safe | impressions/clicks/spend = 0 → 0.0 | ☐ |
| 2.5.5 | Automated tests | `pytest tests/test_metrics.py -v` | ☐ |

```bash
pytest tests/test_metrics.py -v
```

**Manual spot-check one row in DB:**

```bash
python3 << 'EOF'
from app.db.database import SessionLocal
from app.db.models import AdPerformance
db = SessionLocal()
row = db.query(AdPerformance).first()
if row:
    print(f"impressions={row.impressions} clicks={row.clicks} spend={row.spend} revenue={row.revenue}")
    print(f"ctr={row.ctr} (expect {row.clicks/row.impressions if row.impressions else 0:.6f})")
    print(f"cpc={row.cpc} (expect {row.spend/row.clicks if row.clicks else 0:.6f})")
    print(f"roas={row.roas} (expect {row.revenue/row.spend if row.spend else 0:.6f})")
else:
    print("NO ROWS — run ingestion first")
db.close()
EOF
```

Values should match within rounding (6 decimal places).

| Pass? |
|-------|
| ☐ |

### 2.6 Deduplication

| # | Requirement | How to verify | Pass? |
|---|-------------|---------------|-------|
| 2.6.1 | Same record not duplicated | Unique on platform+campaign+ad+date | ☐ |
| 2.6.2 | Re-ingest updates in place | Run ingestion **twice**; row count stable | ☐ |
| 2.6.3 | Automated test | `pytest tests/test_deduplication.py -v` | ☐ |

```bash
# Count before
python3 -c "from app.db.database import SessionLocal; from app.db.models import AdPerformance; db=SessionLocal(); print('count', db.query(AdPerformance).count()); db.close()"

python scripts/ingest_facebook.py

# Count after second run — should NOT double
python scripts/ingest_facebook.py

python3 -c "from app.db.database import SessionLocal; from app.db.models import AdPerformance; db=SessionLocal(); print('count', db.query(AdPerformance).count()); db.close()"
```

**Expected:** Count after 2nd run ≈ count after 1st run (~87 for one platform).

| Pass? |
|-------|
| ☐ |

### 2.7 Persistence & logging

| # | Requirement | How to verify | Pass? |
|---|-------------|---------------|-------|
| 2.7.1 | Data stored persistently | DB file `datads.db` or Postgres has rows | ☐ |
| 2.7.2 | Error handling in poller | `raise_for_retryable_response` + HTTP errors | ☐ |
| 2.7.3 | Basic logging | Ingestion prints INFO lines | ☐ |

### 2.8 Not implemented (document for interview)

| Item | Task says | Your status | Action |
|------|-----------|-------------|--------|
| Google poller | Extensible | Stub only | ☐ Documented in `google.py` |
| TikTok poller | Extensible | Stub only | ☐ Documented in `tiktok.py` |
| Job scheduler | Optional for Part 2 | Manual script | ☐ Explain in interview |
| Proactive rate limiting | Retry on 429 | Reactive only | ☐ Explain in interview |

---

## Part 3 — Query API Layer *(Bonus)*

API base: `http://127.0.0.1:8000`

### 3.1 Server & docs

| # | Check | Command | Expected | Pass? |
|---|-------|---------|----------|-------|
| 3.1.1 | Server health | `curl -s http://127.0.0.1:8000/health` | `{"status":"ok"}` | ☐ |
| 3.1.2 | Root redirect | Browser: `http://127.0.0.1:8000/` | Redirects to `/docs` | ☐ |
| 3.1.3 | Swagger UI | Browser: `http://127.0.0.1:8000/docs` | Interactive docs load | ☐ |
| 3.1.4 | `part_3/README.md` | File exists with curl examples | ☐ |

### 3.2 `GET /api/performance`

| # | Requirement | Command | Pass? |
|---|-------------|---------|-------|
| 3.2.1 | Endpoint works | See below | ☐ |
| 3.2.2 | Filter `platform` | `?platform=facebook` | ☐ |
| 3.2.3 | Filter `date_from`, `date_to` | `?date_from=...&date_to=...` | ☐ |
| 3.2.4 | Filter `campaign_id` | `?campaign_id=fb_camp_123` | ☐ |
| 3.2.5 | Response shape | `data` + `filters_applied` | ☐ |
| 3.2.6 | Aggregates: totals + averages | See field list below | ☐ |

```bash
curl -s "http://127.0.0.1:8000/api/performance?platform=facebook&date_from=$DATE_FROM&date_to=$DATE_TO" \
  | python3 -m json.tool
```

**Expected JSON structure:**

```json
{
  "data": {
    "total_impressions": <number > 0>,
    "total_clicks": <number>,
    "total_spend": <number>,
    "total_revenue": <number>,
    "average_ctr": <number>,
    "average_cpc": <number>,
    "average_roas": <number>
  },
  "filters_applied": {
    "platform": "facebook",
    "date_from": "...",
    "date_to": "...",
    "campaign_id": null
  }
}
```

**Verify average formulas manually:**

```text
average_ctr  ≈ total_clicks / total_impressions
average_cpc  ≈ total_spend / total_clicks
average_roas ≈ total_revenue / total_spend
```

```bash
# Campaign filter — totals should be <= full platform totals
curl -s "http://127.0.0.1:8000/api/performance?platform=facebook&campaign_id=fb_camp_123&date_from=$DATE_FROM&date_to=$DATE_TO" \
  | python3 -m json.tool
```

| Pass? |
|-------|
| ☐ |

### 3.3 `GET /api/top-performing`

| # | Requirement | Command | Pass? |
|---|-------------|---------|-------|
| 3.3.1 | `metric` required | Omit metric → error | ☐ |
| 3.3.2 | Metrics: ctr, cpc, roas, clicks, revenue | Try each | ☐ |
| 3.3.3 | `order` asc/desc (default desc) | `?order=asc` vs `desc` | ☐ |
| 3.3.4 | `limit` default 10, max 100 | `?limit=3`, `?limit=101` → 422 | ☐ |
| 3.3.5 | Filters: platform, dates | Same as performance | ☐ |
| 3.3.6 | Response: `data[]` + `pagination` | See below | ☐ |
| 3.3.7 | Each row has per-ad metrics | ctr, cpc, roas on each item | ☐ |

```bash
# Happy path
curl -s "http://127.0.0.1:8000/api/top-performing?metric=roas&limit=5&platform=facebook&date_from=$DATE_FROM&date_to=$DATE_TO" \
  | python3 -m json.tool

# Missing metric → 422 (FastAPI validation)
curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8000/api/top-performing?platform=facebook"

# Invalid metric → 400
curl -s "http://127.0.0.1:8000/api/top-performing?metric=invalid&platform=facebook" | python3 -m json.tool

# Limit > 100 → 422
curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8000/api/top-performing?metric=roas&limit=101"
```

**Expected status codes:**

| Request | HTTP code |
|---------|-----------|
| Valid query | 200 |
| Missing `metric` | 422 |
| `metric=invalid` | 400 with "Invalid metric" |
| `limit=101` | 422 |
| `date_from` > `date_to` | 400 |

```bash
curl -s "http://127.0.0.1:8000/api/top-performing?metric=roas&date_from=2026-05-16&date_to=2026-04-01" | python3 -m json.tool
```

| Pass? |
|-------|
| ☐ |

### 3.4 API automated tests

```bash
pytest tests/test_api.py -v
```

**Expected:** 4 passed

| Pass? |
|-------|
| ☐ |

### 3.5 Not implemented (bonus)

| Item | Pass? | Notes |
|------|-------|-------|
| Deployed public URL | ☐ N/A | Optional bonus |
| `campaign_id` on top-performing | ☐ N/A | Not in task spec |

---

## Part 4 — Submission *(Required)*

| # | Requirement | How to verify | Pass? |
|---|-------------|---------------|-------|
| 4.1 | Public git repository | `git remote -v` → GitHub URL, repo set Public | ☐ |
| 4.2 | Folder structure | See tree below | ☐ |
| 4.3 | No secrets committed | `.env` not in git; `.env.example` only | ☐ |
| 4.4 | Email to daniel@datads.io | Sent with name, role, repo URL | ☐ |
| 4.5 | Email ≥ 24h before interview | Calendar check | ☐ |

**Required folder tree:**

```text
part_1/
  system_design.png    ✓
  README.md            ✓
part_2/
  README.md            ✓
part_3/
  README.md            ✓
README.md              ✓
requirements.txt       ✓
```

**Gap vs strict spec:** Task asks for `.py` files inside `part_2/` and `part_3/`. Your code lives in `app/`. Root `README.md` explains this — acceptable if documented.

```bash
git status                    # should work after git init
git check-ignore -v .env      # should show .env is ignored
```

| Pass? |
|-------|
| ☐ |

---

## Automated Test Suite (Bonus)

Run the full suite once after manual checks:

```bash
pytest -v
```

| # | Test file | What it proves | Pass? |
|---|-----------|----------------|-------|
| T.1 | `test_metrics.py` | CTR/CPC/ROAS formulas | ☐ |
| T.2 | `test_deduplication.py` | Upsert / unique constraint | ☐ |
| T.3 | `test_facebook_poller.py` | Pagination + retry | ☐ |
| T.4 | `test_api.py` | Validation + endpoints | ☐ |

**Expected:** `13 passed`

---

## Evaluation Focus Areas (Task §395–402)

Self-score before submission:

| Focus area | Evidence in your project | Confident? |
|------------|--------------------------|------------|
| API integration | Facebook poller, pagination, retries | ☐ |
| Data processing | Metrics, normalization, dedup | ☐ |
| System design | part_1 diagram + README | ☐ |
| Data modeling | `ad_performance` table, indexes, unique key | ☐ |
| Code quality | `app/` separation: pollers, services, api, db | ☐ |
| Error handling | retry.py, HTTPException in routes | ☐ |
| Documentation | README, part_1/2/3, this guide | ☐ |

---

## Quick Verification Script

Run all automated checks in one go:

```bash
cd ~/Documents/Projects/DatAds
source venv/bin/activate
export API_BASE="https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io"

echo "=== Mock API ==="
curl -sf "$API_BASE/health" > /dev/null && echo "OK health" || echo "FAIL health"

echo "=== Files ==="
test -f part_1/system_design.png && echo "OK diagram" || echo "FAIL diagram"
test -f part_1/README.md && echo "OK part_1 README" || echo "FAIL part_1"
test -f part_2/README.md && echo "OK part_2 README" || echo "FAIL part_2"
test -f part_3/README.md && echo "OK part_3 README" || echo "FAIL part_3"

echo "=== Tests ==="
pytest -q

echo "=== Local API (if running) ==="
curl -sf http://127.0.0.1:8000/health > /dev/null && echo "OK local API" || echo "SKIP local API (start uvicorn)"
```

---

## Summary Scorecard

Fill in after completing all sections:

| Part | Items | Passed | Failed | N/A |
|------|-------|--------|--------|-----|
| Part 0 — Mock API | 3 | | | |
| Part 1 — Design | 8 | | | |
| Part 2 — Polling | 25+ | | | |
| Part 3 — API | 20+ | | | |
| Part 4 — Submission | 5 | | | |
| Automated tests | 13 | | | |

**Known gaps to acknowledge (not blockers for take-home):**

- Google & TikTok pollers not implemented (stubs only)
- No cloud deployment URL
- No git repo / submission email yet
- Job scheduler documented, not built
- Proactive rate-limit throttling not built (retry-only)

---

## Reference

| Document | Purpose |
|----------|---------|
| `documents/dataAds_task.md` | Official requirements |
| `documents/datads_delivery_plan.md` | Implementation plan |
| `documents/planning.md` | Status tracker |
| `documents/manual_verification_guide.md` | This file |
