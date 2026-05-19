import json
import logging
import signal
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.schemas.ingest_job import IngestCampaignJob, IngestPlatformJob, parse_ingest_job
from app.worker.processor import JobProcessor

logger = logging.getLogger(__name__)


class GracefulShutdown:
    def __init__(self) -> None:
        self.stop = False
        signal.signal(signal.SIGTERM, self._handle)
        signal.signal(signal.SIGINT, self._handle)

    def _handle(self, signum: int, _frame: Any) -> None:
        logger.info("Received signal %s; finishing current message then exiting", signum)
        self.stop = True


class SqsIngestConsumer:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.sqs_queue_url:
            raise ValueError("SQS_QUEUE_URL is required for the ingestion worker")

        self.queue_url = settings.sqs_queue_url
        self.wait_time_seconds = settings.sqs_wait_time_seconds
        self.max_messages = settings.sqs_max_messages
        self._sqs = boto3.client("sqs", region_name=settings.aws_region)
        self._shutdown = GracefulShutdown()

    def run_forever(self) -> None:
        logger.info("Starting SQS consumer on %s", self.queue_url)
        while not self._shutdown.stop:
            try:
                response = self._sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=self.max_messages,
                    WaitTimeSeconds=self.wait_time_seconds,
                    AttributeNames=["ApproximateReceiveCount"],
                )
            except (BotoCoreError, ClientError):
                logger.exception("Failed to receive messages from SQS")
                continue

            messages = response.get("Messages", [])
            if not messages:
                continue

            for message in messages:
                if self._shutdown.stop:
                    break
                self._handle_message(message)

        logger.info("SQS consumer stopped")

    def _handle_message(self, message: dict) -> None:
        receipt_handle = message["ReceiptHandle"]
        receive_count = message.get("Attributes", {}).get("ApproximateReceiveCount", "?")

        try:
            body = json.loads(message["Body"])
            if isinstance(body, dict) and "Message" in body and isinstance(body["Message"], str):
                body = json.loads(body["Message"])
            job = parse_ingest_job(body)
        except (json.JSONDecodeError, ValueError, TypeError):
            logger.exception("Invalid message body; leaving on queue for DLQ")
            return

        db = SessionLocal()
        try:
            processor = JobProcessor(db)
            if isinstance(job, IngestPlatformJob):
                result = processor.process_platform(job)
            else:
                result = processor.process_campaign(job)
            db.commit()
            logger.info("Job succeeded (receive_count=%s): %s", receive_count, result)
        except Exception:
            db.rollback()
            logger.exception(
                "Job failed (receive_count=%s); message will become visible again",
                receive_count,
            )
            return
        finally:
            db.close()

        try:
            self._sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )
        except (BotoCoreError, ClientError):
            logger.exception("Failed to delete message; risk of duplicate processing")
