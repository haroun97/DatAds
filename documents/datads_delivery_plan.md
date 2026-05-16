# DatAds Take-Home Exercise — Full Delivery Plan

## Goal

Build a professional backend system for the DatAds take-home assignment.

The system will:

1. Fetch ad performance data from external mock ad platform APIs.
2. Handle pagination, rate limits, retries, and API failures.
3. Normalize different platform response formats into one common data model.
4. Store the data in PostgreSQL.
5. Deduplicate records safely.
6. Calculate CTR, CPC, and ROAS.
7. Expose REST API endpoints to query aggregated ad performance.
8. Include tests, documentation, and optional deployment.

The final result should look like a clean, production-minded backend project that is still simple enough for a take-home assignment.

---

# 1. Metrics Explanation

## CTR — Click-Through Rate

CTR tells us how many people clicked the ad after seeing it.

```text
CTR = clicks / impressions
```

Example:

```text
clicks = 100
impressions = 10,000

CTR = 100 / 10,000 = 0.01 = 1%
```

A higher CTR usually means the ad creative is interesting or relevant.

---

## CPC — Cost Per Click

CPC tells us how much we paid for each click.

```text
CPC = spend / clicks
```

Example:

```text
spend = 50
clicks = 100

CPC = 50 / 100 = 0.50
```

This means each click costs $0.50.

---

## ROAS — Return On Ad Spend

ROAS tells us how much revenue we made for every dollar spent.

```text
ROAS = revenue / spend
```

Example:

```text
revenue = 500
spend = 100

ROAS = 500 / 100 = 5
```

This means every $1 spent generated $5 revenue.

---

# 2. Chosen Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3.12 |
| API Framework | FastAPI |
| HTTP Client | httpx |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Validation | Pydantic |
| Testing | pytest |
| Retry Logic | tenacity |
| Server | uvicorn |
| Containerization | Docker + Docker Compose |
| Deployment | Render or Railway |

---

# 3. Why This Stack?

## Python 3.12

Python is fast to develop with, easy to read, and very strong for backend/data processing tasks.

It is a good fit because this project needs:

- API integration
- data transformation
- database persistence
- metric calculation
- REST API development
- testing

Python keeps the solution simple and readable.

---

## FastAPI

FastAPI is a modern Python framework for building APIs.

I chose it because:

- it is fast to implement
- it has automatic API documentation
- it works very well with Pydantic validation
- it gives clean request/response models
- it is professional and production-friendly

FastAPI automatically provides:

```text
/docs
```

This is useful for the reviewer because they can test the API easily.

---

## httpx

httpx is used to call the external mock ad APIs.

I chose it because:

- it supports timeouts
- it has a clean API
- it supports async requests if we want to scale later
- it works well with retry logic

---

## PostgreSQL

PostgreSQL is used instead of SQLite.

I chose PostgreSQL because:

- it is closer to a real production database
- it supports strong constraints
- it handles concurrent reads/writes better than SQLite
- it supports indexing for API filters
- it is easy to deploy on Render or Railway
- it shows better backend engineering judgment

PostgreSQL is a better fit for a system that may grow to many platforms, many campaigns, and many records.

---

## SQLAlchemy

SQLAlchemy is used as the ORM/database layer.

I chose it because:

- it keeps database code organized
- it avoids raw SQL everywhere
- it makes models clear
- it works with PostgreSQL
- it keeps the app flexible if the database changes later

---

## Alembic

Alembic is used for database migrations.

I chose it because:

- it is the standard migration tool with SQLAlchemy
- it lets us version database schema changes
- it looks professional
- it avoids manually recreating tables

Example:

```bash
alembic revision --autogenerate -m "create ad performance table"
alembic upgrade head
```

---

## Pydantic

Pydantic is used for validation and schemas.

I chose it because:

- it validates API inputs
- it validates API outputs
- it works naturally with FastAPI
- it makes code safer and clearer

---

## pytest

pytest is used for testing.

I chose it because:

- it is simple
- it is widely used
- it works well for unit and integration tests
- it helps prove that metrics, deduplication, and API filters work

---

## tenacity

tenacity is used for retry logic.

I chose it because:

- it makes retries clean
- it supports exponential backoff
- it handles temporary API failures
- it is useful for 429 and 5xx errors

---

## uvicorn

uvicorn runs the FastAPI app.

I chose it because it is the standard ASGI server for FastAPI.

---

## Docker Compose

Docker Compose is used to run PostgreSQL locally.

I chose it because:

- it avoids manual PostgreSQL installation
- reviewers can run the project easily
- it makes the setup consistent

---

# 4. Final Repository Structure

```text
datads-takehome/
│
├── README.md
├── docker-compose.yml
├── .env.example
├── requirements.txt
│
├── part_1/
│   ├── README.md
│   └── system_design.png
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repositories.py
│   │
│   ├── schemas/
│   │   ├── ad_performance.py
│   │   └── api_responses.py
│   │
│   ├── pollers/
│   │   ├── base.py
│   │   ├── facebook.py
│   │   ├── google.py
│   │   └── tiktok.py
│   │
│   ├── services/
│   │   ├── ingestion_service.py
│   │   ├── metrics_service.py
│   │   └── analytics_service.py
│   │
│   ├── api/
│   │   ├── routes.py
│   │   └── dependencies.py
│   │
│   └── utils/
│       ├── dates.py
│       └── retry.py
│
├── alembic/
│   └── versions/
│
├── alembic.ini
│
├── scripts/
│   ├── ingest_facebook.py
│   └── seed_data.py
│
├── tests/
│   ├── test_metrics.py
│   ├── test_deduplication.py
│   ├── test_facebook_poller.py
│   └── test_api.py
│
├── part_2/
│   └── README.md
│
└── part_3/
    └── README.md
```

This structure is cleaner than separating completely different apps for part 2 and part 3.

In the README, explain that:

```text
app/ contains the working implementation for Part 2 and Part 3.
part_1/, part_2/, and part_3/ contain task-specific documentation.
```

---

# 5. Architecture — Take-Home Version

```text
Scheduler / Manual Script
   ↓
Platform Pollers
   ↓
Normalization Layer
   ↓
Deduplication Layer
   ↓
PostgreSQL
   ↓
Aggregation Layer
   ↓
REST API
```

---

## 5.1 Scheduler / Manual Script

For the take-home task, we do not need to build a full scheduler.

Instead, we provide a script:

```bash
python scripts/ingest_facebook.py
```

This script manually starts the ingestion process.

In production, this could become:

- cron job
- Celery Beat
- Airflow DAG
- cloud scheduler

Simple explanation:

```text
The scheduler decides when we should fetch fresh ad data.
For this assignment, I trigger ingestion manually with a script.
```

---

## 5.2 Platform Pollers

Each platform has its own poller.

Example:

```text
FacebookPoller
GooglePoller
TikTokPoller
```

Why?

Because every platform has different:

- endpoint URLs
- authentication headers
- pagination style
- field names
- rate limits
- response shape

The poller is responsible for talking to that platform.

Simple explanation:

```text
A poller is a small class that knows how to fetch data from one ad platform.
```

---

## 5.3 Normalization Layer

The platforms return different field names.

Facebook:

```text
spend
revenue
clicks
impressions
```

Google:

```text
cost
conversionValue
clicks
impressions
```

TikTok:

```text
budget_spent
purchase_value
engagements
views
```

The normalization layer converts all of them to one common format:

```text
platform
campaign_id
ad_id
date
impressions
clicks
spend
conversions
revenue
```

Simple explanation:

```text
Normalization makes different platform data look the same inside our system.
```

This is one of the most important design decisions.

---

## 5.4 Deduplication Layer

The same data may be fetched more than once.

Example:

```text
We fetch Facebook data for the last 30 days today.
Tomorrow we fetch the last 30 days again.
Many records overlap.
```

We prevent duplicates using a unique database constraint:

```text
platform + campaign_id + ad_id + date
```

If the same record is inserted again, PostgreSQL prevents duplication.

Simple explanation:

```text
Deduplication keeps the database clean when we fetch the same data multiple times.
```

---

## 5.5 PostgreSQL

PostgreSQL stores the normalized records.

It gives us:

- persistent storage
- constraints
- indexes
- filtering
- aggregation queries
- production-like setup

Simple explanation:

```text
PostgreSQL is where we save the clean ad performance data.
```

---

## 5.6 Aggregation Layer

The aggregation layer calculates summary results.

Example:

```text
total impressions
total clicks
total spend
total revenue
average CTR
average CPC
average ROAS
```

It also handles top-performing ads.

Simple explanation:

```text
The aggregation layer prepares useful insights from the stored data.
```

---

## 5.7 REST API

The REST API lets users query performance data.

Endpoints:

```http
GET /api/performance
GET /api/top-performing
```

Simple explanation:

```text
The API is how users or dashboards ask for insights.
```

---

# 6. Production Architecture

```text
Scheduler
   ↓
Message Queue
   ↓
Worker Pool
   ↓
Raw Data Store
   ↓
Analytics DB
   ↓
Caching Layer
   ↓
API Layer
```

This is the scalable version.

---

## 6.1 Scheduler

The scheduler creates jobs.

Example:

```text
Fetch Facebook campaign data every hour.
Fetch Google campaign data every two hours.
Fetch TikTok campaign data every three hours.
```

---

## 6.2 Message Queue

The queue stores jobs before they are processed.

Example jobs:

```text
fetch_facebook_campaign_123
fetch_facebook_campaign_456
fetch_google_reports
fetch_tiktok_performance
```

Why use a queue?

- prevents overload
- allows retries
- allows parallel processing
- keeps jobs safe if workers crash

Possible tools:

```text
SQS
RabbitMQ
Kafka
Redis Queue
Celery
```

---

## 6.3 Worker Pool

Workers take jobs from the queue and execute them.

Example:

```text
Worker 1 fetches Facebook data.
Worker 2 fetches Google data.
Worker 3 fetches TikTok data.
```

If we need more speed, we add more workers.

Simple explanation:

```text
Workers do the actual fetching and processing work.
```

---

## 6.4 Raw Data Store

This stores original API responses.

Why keep raw data?

- debugging
- reprocessing
- audit trail
- fixing bugs later
- comparing original data with processed data

Possible storage:

```text
S3
GCS
Azure Blob Storage
PostgreSQL JSONB
```

---

## 6.5 Analytics DB

This stores clean data optimized for queries.

For medium scale:

```text
PostgreSQL
```

For large scale:

```text
ClickHouse
BigQuery
Redshift
Snowflake
```

Simple explanation:

```text
The analytics database is optimized for fast reporting and dashboards.
```

---

## 6.6 Caching Layer

Cache stores common query results.

Example:

```text
Last 30 days performance for Facebook
Top 10 ads by ROAS
```

Why use cache?

- faster responses
- less database load
- supports more API traffic

Possible tool:

```text
Redis
```

---

## 6.7 API Layer

The API layer serves users and dashboards.

Important point:

```text
The API should not call external ad APIs directly.
It should read from our database or cache.
```

This makes the API fast and reliable.

---

# 7. PostgreSQL Database Design

## Main Table: ad_performance

```sql
CREATE TABLE ad_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    platform VARCHAR(50) NOT NULL,
    campaign_id VARCHAR(255) NOT NULL,
    ad_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,

    impressions INTEGER NOT NULL DEFAULT 0,
    clicks INTEGER NOT NULL DEFAULT 0,
    spend NUMERIC(12, 2) NOT NULL DEFAULT 0,
    conversions INTEGER NOT NULL DEFAULT 0,
    revenue NUMERIC(12, 2) NOT NULL DEFAULT 0,

    ctr NUMERIC(12, 6) NOT NULL DEFAULT 0,
    cpc NUMERIC(12, 6) NOT NULL DEFAULT 0,
    roas NUMERIC(12, 6) NOT NULL DEFAULT 0,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_ad_performance UNIQUE (
        platform,
        campaign_id,
        ad_id,
        date
    )
);
```

---

## Recommended Indexes

```sql
CREATE INDEX idx_ad_performance_platform
ON ad_performance(platform);

CREATE INDEX idx_ad_performance_date
ON ad_performance(date);

CREATE INDEX idx_ad_performance_campaign
ON ad_performance(campaign_id);

CREATE INDEX idx_ad_performance_platform_date
ON ad_performance(platform, date);

CREATE INDEX idx_ad_performance_roas
ON ad_performance(roas);

CREATE INDEX idx_ad_performance_ctr
ON ad_performance(ctr);

CREATE INDEX idx_ad_performance_cpc
ON ad_performance(cpc);
```

Why indexes?

They make filters and sorting faster.

The API filters by:

- platform
- date range
- campaign

The top-performing endpoint sorts by:

- ctr
- cpc
- roas
- clicks
- revenue

---

# 8. Data Flow

## Example Facebook Flow

```text
1. Run ingestion script.
2. FacebookPoller calls the Facebook-like mock API.
3. Poller sends campaign ID, since date, until date, and pagination cursor.
4. API returns records.
5. Poller follows paging.next until no more pages exist.
6. Each record is normalized.
7. Metrics are calculated.
8. Record is saved to PostgreSQL.
9. Duplicate records are ignored or updated.
10. API can now query the stored data.
```

---

# 9. Mock API Implementation Plan

## Start With Facebook

Implement Facebook fully first.

Why Facebook?

- clear endpoint
- clear campaign IDs
- cursor pagination
- good enough to demonstrate the full pipeline

Available campaigns:

```text
fb_camp_123
fb_camp_456
fb_camp_789
```

Endpoint:

```http
GET /api/v1/campaigns/{campaign_id}/insights
```

Headers:

```text
x-api-key: facebook_test_key_123
```

Query params:

```text
since
until
limit
after
```

Pagination:

```text
paging.next
```

---

## Add Extensibility for Google and TikTok

Even if not fully implemented, add files:

```text
google.py
tiktok.py
```

Inside them, document or partially implement how the mapping works.

Google mapping:

```text
campaignId          -> campaign_id
adId                -> ad_id
metrics.impressions -> impressions
metrics.clicks      -> clicks
metrics.cost        -> spend
metrics.conversionValue -> revenue
```

TikTok mapping:

```text
campaign.id                  -> campaign_id
campaign.ad_id               -> ad_id
performance.views            -> impressions
performance.engagements      -> clicks
performance.budget_spent     -> spend
performance.purchase_value   -> revenue
```

This shows the reviewer that the design can scale to more platforms.

---

# 10. Retry and Rate Limit Plan

The mock APIs can return:

```text
429 rate limit
500 random server errors
network timeouts
```

The system should retry these.

Retryable statuses:

```text
429
500
502
503
504
```

Retry strategy:

```text
attempt 1: immediate
attempt 2: wait 2 seconds
attempt 3: wait 4 seconds
attempt 4: wait 8 seconds
```

Use exponential backoff.

Simple explanation:

```text
If the API fails temporarily, we wait and try again instead of failing immediately.
```

---

# 11. Metric Calculation Plan

Create functions:

```python
def calculate_ctr(clicks: int, impressions: int) -> float:
    if impressions == 0:
        return 0
    return clicks / impressions


def calculate_cpc(spend: float, clicks: int) -> float:
    if clicks == 0:
        return 0
    return spend / clicks


def calculate_roas(revenue: float, spend: float) -> float:
    if spend == 0:
        return 0
    return revenue / spend
```

Why handle zero?

Because division by zero would crash the app.

---

# 12. Ingestion Script Plan

Create:

```text
scripts/ingest_facebook.py
```

It should:

1. calculate last 30 days
2. loop through Facebook campaign IDs
3. fetch all pages
4. normalize records
5. calculate metrics
6. save to PostgreSQL
7. print summary

Example output:

```text
Starting Facebook ingestion...
Date range: 2026-04-16 to 2026-05-16

Campaign fb_camp_123:
Fetched 120 records
Inserted 120 records
Skipped duplicates 0

Campaign fb_camp_456:
Fetched 100 records
Inserted 98 records
Skipped duplicates 2

Done.
Total fetched: 220
Total inserted: 218
Total duplicates: 2
```

---

# 13. API Layer Plan

Build two endpoints.

---

## Endpoint 1: GET /api/performance

Purpose:

Return aggregated performance metrics.

Query params:

```text
platform optional
date_from optional
date_to optional
campaign_id optional
```

Example:

```bash
curl "http://localhost:8000/api/performance?platform=facebook&date_from=2026-04-16&date_to=2026-05-16"
```

Response:

```json
{
  "data": {
    "total_impressions": 50000,
    "total_clicks": 1200,
    "total_spend": 500.75,
    "total_revenue": 2400.00,
    "average_ctr": 0.024,
    "average_cpc": 0.417,
    "average_roas": 4.79
  },
  "filters_applied": {
    "platform": "facebook",
    "date_from": "2026-04-16",
    "date_to": "2026-05-16"
  }
}
```

Important:

For totals:

```text
SUM(impressions)
SUM(clicks)
SUM(spend)
SUM(revenue)
```

For average metrics, better calculate from totals:

```text
average_ctr = total_clicks / total_impressions
average_cpc = total_spend / total_clicks
average_roas = total_revenue / total_spend
```

This is better than averaging row-level CTR/CPC/ROAS.

---

## Endpoint 2: GET /api/top-performing

Purpose:

Return best ads sorted by selected metric.

Query params:

```text
metric required: ctr, cpc, roas, clicks, revenue
order optional: asc or desc
limit optional: default 10, max 100
platform optional
date_from optional
date_to optional
```

Example:

```bash
curl "http://localhost:8000/api/top-performing?metric=roas&limit=10&platform=facebook"
```

Response:

```json
{
  "data": [
    {
      "ad_id": "fb_ad_456",
      "campaign_id": "fb_camp_123",
      "platform": "facebook",
      "date": "2026-05-01",
      "impressions": 10000,
      "clicks": 150,
      "spend": 75.50,
      "revenue": 360.00,
      "ctr": 0.015,
      "cpc": 0.503,
      "roas": 4.768
    }
  ],
  "pagination": {
    "limit": 10,
    "total": 150
  }
}
```

---

# 14. Input Validation Plan

Validate:

## metric

Allowed:

```text
ctr
cpc
roas
clicks
revenue
```

If invalid:

```json
{
  "detail": "Invalid metric. Allowed values: ctr, cpc, roas, clicks, revenue"
}
```

---

## order

Allowed:

```text
asc
desc
```

---

## limit

Rules:

```text
default = 10
max = 100
min = 1
```

---

## dates

Format:

```text
YYYY-MM-DD
```

If date_from is after date_to, return error.

---

# 15. Docker Compose Plan

Create:

```text
docker-compose.yml
```

Example:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: datads-postgres
    environment:
      POSTGRES_USER: datads
      POSTGRES_PASSWORD: datads
      POSTGRES_DB: datads
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Create:

```text
.env.example
```

Example:

```env
DATABASE_URL=postgresql+psycopg://datads:datads@localhost:5432/datads
API_BASE_URL=https://datads-mock-ad-apis.happygrass-47d99234.germanywestcentral.azurecontainerapps.io
FACEBOOK_API_KEY=facebook_test_key_123
GOOGLE_TOKEN=google_test_token_456
TIKTOK_TOKEN=tiktok_test_token_789
```

---

# 16. Requirements Plan

Create:

```text
requirements.txt
```

Recommended dependencies:

```text
fastapi
uvicorn[standard]
httpx
sqlalchemy
psycopg[binary]
alembic
pydantic
pydantic-settings
python-dotenv
tenacity
pytest
pytest-asyncio
respx
```

---

# 17. Testing Plan

## Test 1 — Metrics

File:

```text
tests/test_metrics.py
```

Test:

```text
CTR normal case
CTR zero impressions
CPC normal case
CPC zero clicks
ROAS normal case
ROAS zero spend
```

---

## Test 2 — Deduplication

File:

```text
tests/test_deduplication.py
```

Test:

```text
Insert same platform + campaign + ad + date twice.
Verify only one record exists.
```

---

## Test 3 — Poller Pagination

File:

```text
tests/test_facebook_poller.py
```

Mock two pages:

```text
page 1 has paging.next
page 2 has no paging.next
```

Verify both pages are fetched.

---

## Test 4 — Retry Logic

Mock:

```text
first request returns 500
second request returns 200
```

Verify poller eventually succeeds.

---

## Test 5 — API Validation

File:

```text
tests/test_api.py
```

Test:

```text
invalid metric returns error
limit over 100 returns error
valid performance query returns expected shape
```

---

# 18. Documentation Plan

## Root README.md

Include:

1. project overview
2. architecture summary
3. tech stack
4. how to run locally
5. how to run PostgreSQL
6. how to run migrations
7. how to ingest data
8. how to run API
9. example curl commands
10. how to run tests
11. production improvements
12. AI usage note

---

## part_1/README.md

Include:

- architecture diagram
- explanation
- reliability strategy
- scalability strategy
- failure handling
- production design

---

## part_2/README.md

Include:

- ingestion implementation details
- Facebook API implementation
- pagination handling
- retry handling
- deduplication strategy
- metrics calculation
- sample output

---

## part_3/README.md

Include:

- API routes
- query parameters
- example responses
- validation rules
- curl examples
- deployment URL if available

---

# 19. Run Commands

## Start PostgreSQL

```bash
docker compose up -d
```

---

## Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Setup Environment

```bash
cp .env.example .env
```

---

## Run Migrations

```bash
alembic upgrade head
```

---

## Ingest Facebook Data

```bash
python scripts/ingest_facebook.py
```

---

## Start API Server

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

---

## Run Tests

```bash
pytest
```

---

# 20. Deployment Plan

Use Render or Railway.

## Recommended Deployment Setup

Deploy:

- FastAPI web service
- PostgreSQL database

Environment variables:

```text
DATABASE_URL
API_BASE_URL
FACEBOOK_API_KEY
GOOGLE_TOKEN
TIKTOK_TOKEN
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

After deployment, provide:

```text
API docs URL
GitHub repository URL
```

Example:

```text
https://datads-takehome.onrender.com/docs
```

---

# 21. Final Submission Checklist

## Part 1

- [ ] system_design.png
- [ ] part_1/README.md
- [ ] architecture explanation
- [ ] scalability explanation
- [ ] reliability explanation

---

## Part 2

- [ ] Facebook poller
- [ ] pagination
- [ ] retry logic
- [ ] PostgreSQL persistence
- [ ] deduplication
- [ ] metrics calculation
- [ ] ingestion script
- [ ] sample output
- [ ] part_2/README.md

---

## Part 3 Bonus

- [ ] FastAPI app
- [ ] GET /api/performance
- [ ] GET /api/top-performing
- [ ] input validation
- [ ] error handling
- [ ] curl examples
- [ ] part_3/README.md

---

## Testing

- [ ] metric tests
- [ ] deduplication tests
- [ ] poller pagination tests
- [ ] retry tests
- [ ] API validation tests

---

## Deployment Bonus

- [ ] deployed API
- [ ] public /docs URL
- [ ] environment variables configured
- [ ] deployment URL added to README

---

## Final GitHub Repo

- [ ] public repository
- [ ] clean folder structure
- [ ] README complete
- [ ] no secrets committed
- [ ] .env ignored
- [ ] requirements.txt included
- [ ] docker-compose.yml included
- [ ] tests included

---

# 22. Interview Talking Points

## Why PostgreSQL instead of SQLite?

Answer:

```text
I chose PostgreSQL because it is closer to production.
It supports stronger constraints, better concurrency, indexing, and deployment.
SQLite would be enough for a small demo, but PostgreSQL better matches the scale and reliability requirements of this task.
```

---

## Why use pollers?

Answer:

```text
Each ad platform has different APIs, pagination, authentication, and response fields.
Pollers isolate those differences so the rest of the system can stay clean and platform-independent.
```

---

## Why normalize data?

Answer:

```text
Normalization converts different platform formats into one internal model.
This makes storage, metrics, and API queries much simpler.
```

---

## How do you handle duplicates?

Answer:

```text
I use a unique PostgreSQL constraint on platform, campaign_id, ad_id, and date.
This makes ingestion idempotent, so fetching the same data again does not create duplicate rows.
```

---

## How do you handle API failures?

Answer:

```text
I use timeouts, retry logic, and exponential backoff for temporary failures such as 429 and 5xx responses.
```

---

## How would this scale?

Answer:

```text
I would separate ingestion from the API.
A scheduler would create jobs, a queue would store them, workers would process them, and the API would read from an analytics database or cache.
```

---

## How would you support thousands of API requests per second?

Answer:

```text
I would use caching, pre-aggregated tables, read replicas, and possibly a specialized analytics database like ClickHouse for large-scale reporting.
```

---

## Why calculate average CTR from totals?

Answer:

```text
For aggregate reporting, calculating CTR as total_clicks / total_impressions is more accurate than averaging individual row CTR values.
```

---

# 23. Recommended Delivery Order

## Step 1

Create repo and folder structure.

## Step 2

Add Docker Compose PostgreSQL setup.

## Step 3

Add SQLAlchemy models and Alembic migration.

## Step 4

Add metric calculation functions.

## Step 5

Implement Facebook poller.

## Step 6

Implement ingestion service and script.

## Step 7

Test ingestion and save records to PostgreSQL.

## Step 8

Implement FastAPI routes.

## Step 9

Add tests.

## Step 10

Write documentation.

## Step 11

Create architecture diagram.

## Step 12

Deploy API.

## Step 13

Final cleanup and submit GitHub URL.

---

# 24. AI Usage Note

Add this to the README:

```text
AI tools were used to help structure the implementation plan, refine documentation, and review architectural tradeoffs. The final implementation decisions, code organization, and submitted solution were reviewed and adapted by me.
```

---

# 25. Final Submission Email

Send the GitHub link to:

```text
daniel@datads.io
```

Email should include:

```text
name
role
GitHub repository URL
deployment URL if available
short note that the solution includes Parts 1, 2, and bonus Part 3
```

---

# Final Goal

The final submission should demonstrate:

- clean backend design
- reliable API integration
- good database modeling
- strong error handling
- simple but scalable architecture
- useful documentation
- production awareness
- ability to explain tradeoffs clearly in the interview

This is the target: professional, practical, and easy to review.
