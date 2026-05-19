#!/usr/bin/env python3
"""Move messages from the DLQ back to the main ingest queue."""

import argparse
import sys
from pathlib import Path

import boto3

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay DLQ messages to the main queue")
    parser.add_argument("--max", type=int, default=10, help="Max messages to replay")
    args = parser.parse_args()

    settings = get_settings()
    if not settings.sqs_queue_url or not settings.sqs_dlq_url:
        print("Set SQS_QUEUE_URL and SQS_DLQ_URL in .env", file=sys.stderr)
        sys.exit(1)

    client = boto3.client("sqs", region_name=settings.aws_region)
    replayed = 0

    while replayed < args.max:
        response = client.receive_message(
            QueueUrl=settings.sqs_dlq_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1,
        )
        messages = response.get("Messages", [])
        if not messages:
            break

        message = messages[0]
        client.send_message(
            QueueUrl=settings.sqs_queue_url,
            MessageBody=message["Body"],
        )
        client.delete_message(
            QueueUrl=settings.sqs_dlq_url,
            ReceiptHandle=message["ReceiptHandle"],
        )
        replayed += 1
        print(f"Replayed message {message['MessageId']}")

    print(f"Done. Replayed {replayed} message(s).")


if __name__ == "__main__":
    main()
