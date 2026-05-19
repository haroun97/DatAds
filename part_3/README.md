# Part 3 — Query API Layer (Bonus)

Implementation: `app/api/routes.py`, `app/services/analytics_service.py`, `app/main.py`

## Live Deployment

The API is deployed on **Render**:

| | |
|---|---|
| **Swagger UI** | https://datads.onrender.com/docs |
| **Health check** | https://datads.onrender.com/health |
| **Performance** | https://datads.onrender.com/api/performance |
| **Top performing** | https://datads.onrender.com/api/top-performing?metric=roas |

> Note: Render free tier spins down after inactivity — the first request may take ~30 seconds to wake up.

## Run Locally

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## Endpoints

### `GET /api/performance`

Returns aggregated metrics for all matching records.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `platform` | No | e.g. `facebook` |
| `date_from` | No | YYYY-MM-DD |
| `date_to` | No | YYYY-MM-DD |
| `campaign_id` | No | Filter by campaign |

```bash
curl "http://localhost:8000/api/performance?platform=facebook&date_from=2026-04-17&date_to=2026-05-16"
```

Example response:

```json
{
  "data": {
    "total_impressions": 1234567,
    "total_clicks": 12345,
    "total_spend": 5432.10,
    "total_revenue": 25000.00,
    "average_ctr": 0.01,
    "average_cpc": 0.44,
    "average_roas": 4.60
  },
  "filters_applied": {
    "platform": "facebook",
    "date_from": "2026-04-17",
    "date_to": "2026-05-16",
    "campaign_id": null
  }
}
```

### `GET /api/top-performing`

Returns top ads sorted by a metric.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `metric` | **Yes** | — | `ctr`, `cpc`, `roas`, `clicks`, `revenue` |
| `order` | No | `desc` | `asc` or `desc` |
| `limit` | No | `10` | Max 100 |
| `platform` | No | — | Filter by platform |
| `date_from` | No | — | YYYY-MM-DD |
| `date_to` | No | — | YYYY-MM-DD |

```bash
curl "http://localhost:8000/api/top-performing?metric=roas&limit=5&platform=facebook&order=desc"
```

Example response:

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
    "limit": 5,
    "total": 87
  }
}
```

## Validation

- Invalid `metric` → `400` with allowed values listed
- `limit` > 100 → `422`
- `date_from` > `date_to` → `400`

## Tests

```bash
source venv/bin/activate
pytest tests/test_api.py -v
```

Or test the live deployment directly:

```bash
curl "https://datads.onrender.com/api/performance?platform=facebook"
curl "https://datads.onrender.com/api/top-performing?metric=roas&limit=5"
```
