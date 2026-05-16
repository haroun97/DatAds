# Part 3 — Query API Layer (Bonus)

Implementation: `app/api/routes.py`, `app/services/analytics_service.py`, `app/main.py`

## Run the API

```bash
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

## Validation

- Invalid `metric` → `400` with allowed values listed
- `limit` > 100 → `422`
- `date_from` > `date_to` → `400`

## Tests

```bash
pytest tests/test_api.py
```
