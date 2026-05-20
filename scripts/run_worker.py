#!/usr/bin/env python3
"""Long-running SQS consumer for scheduled ingestion jobs."""

# Entrypoint for the background worker container (see Dockerfile.worker).
# Requires SQS_QUEUE_URL to be set in the environment.

import sys
from pathlib import Path

# Make the project root importable when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.logging import setup_logging
from app.worker.sqs_consumer import SqsIngestConsumer


def main() -> None:
    setup_logging()
    # Starts the poll loop — runs until SIGTERM or SIGINT is received.
    SqsIngestConsumer().run_forever()


if __name__ == "__main__":
    main()
