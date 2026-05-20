#!/usr/bin/env python3
"""Send a test ingest job to SQS (Phase 1 manual verification)."""

# Use this script to manually enqueue an ingestion job for testing the worker end-to-end.
# Usage: python scripts/sqs_send_test_job.py --platform facebook --lookback-days 7
# Requires: SQS_QUEUE_URL set in .env and valid AWS credentials.

import argparse
import json
import sys
from pathlib import Path

import boto3

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.schemas.ingest_job import IngestPlatformJob


def main() -> None:
    parser = argparse.ArgumentParser(description="Enqueue a test ingest_platform job")
    parser.add_argument("--platform", default="facebook")
    parser.add_argument("--lookback-days", type=int, default=30)
    args = parser.parse_args()

    settings = get_settings()
    if not settings.sqs_queue_url:
        print("Set SQS_QUEUE_URL in .env", file=sys.stderr)
        sys.exit(1)

    job = IngestPlatformJob(platform=args.platform, lookback_days=args.lookback_days)
    client = boto3.client("sqs", region_name=settings.aws_region)
    response = client.send_message(
        QueueUrl=settings.sqs_queue_url,
        MessageBody=job.model_dump_json(),
    )
    print(f"Sent job_id={job.job_id} message_id={response['MessageId']}")


if __name__ == "__main__":
    main()
