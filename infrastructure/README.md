# AWS ingestion pipeline

EventBridge Scheduler → SQS → ECS Fargate workers → PostgreSQL.

## Job contract (Phase 0)

**`ingest_platform`** — one platform, all campaigns (scheduler default):

```json
{
  "job_type": "ingest_platform",
  "platform": "facebook",
  "lookback_days": 30
}
```

**`ingest_campaign`** — single campaign (manual / future fan-out):

```json
{
  "job_type": "ingest_campaign",
  "platform": "facebook",
  "campaign_id": "fb_camp_123",
  "since": "2026-04-19",
  "until": "2026-05-18"
}
```

Database: keep **Render Postgres** (`DATABASE_URL` on workers) or point `database_url` at RDS.

## Prerequisites

- AWS CLI configured (`aws sts get-caller-identity`)
- If you use **`aws login`** (credentials under `~/.aws/login/`), Terraform cannot read that directly. Use the helper script below or export credentials first.
- Terraform ≥ 1.5
- Docker
- `DATABASE_URL` for your Render (or RDS) instance

## Deploy

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — set database_url and secrets

terraform init

# Option A — aws login users (recommended)
../../scripts/terraform_with_aws.sh apply

# Option B — classic access keys in ~/.aws/credentials
terraform apply
```

Copy outputs into `.env` for local scripts:

```bash
SQS_QUEUE_URL=<terraform output sqs_queue_url>
SQS_DLQ_URL=<terraform output sqs_dlq_url>
AWS_REGION=eu-central-1
```

Build and run the worker on ECS:

```bash
chmod +x scripts/deploy_worker_aws.sh
./scripts/deploy_worker_aws.sh
```

## Phase 1 — verify queue (skipped local worker per request)

```bash
pip install -r requirements.txt
python scripts/sqs_send_test_job.py
```

With ECS running, the worker should process the message. Check CloudWatch Logs (`cloudwatch_log_group` output).

## Schedules (Phase 3)

| Schedule | Default | Notes |
|----------|---------|--------|
| Facebook | `rate(1 hour)` | Active |
| Google | `rate(2 hours)` | Off until poller implemented |
| TikTok | `rate(3 hours)` | Off until poller implemented |

## Operations (Phase 5)

- **DLQ alarm** → SNS topic `datads-prod-alerts` (subscribe email in AWS Console)
- **Replay DLQ:** `python scripts/replay_dlq.py --max 10`
- **Logs:** `aws logs tail /ecs/datads-prod-worker --follow`

## Architecture

```text
EventBridge Scheduler
        ↓
   SQS (ingest-jobs) ──→ DLQ (after 3 failures)
        ↓
   ECS Fargate (run_worker.py)
        ↓
   PostgreSQL (Render/RDS)
```

FastAPI on Render is unchanged; it only reads the database.
