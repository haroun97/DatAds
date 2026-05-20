# Retry logic for outbound HTTP calls to ad-platform APIs.
# Uses tenacity to automatically retry on rate-limits (429), server errors (5xx),
# and transient network failures with exponential backoff.

import logging

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Status codes that indicate a temporary problem and warrant a retry.
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class RetryableAPIError(Exception):
    # Raised manually when we receive a retryable HTTP status so tenacity can catch it.
    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        super().__init__(message or f"Retryable API error: {status_code}")


def is_retryable(exc: BaseException) -> bool:
    # Tell tenacity which exception types should trigger a retry attempt.
    if isinstance(exc, httpx.TimeoutException | httpx.NetworkError):
        return True
    if isinstance(exc, RetryableAPIError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS_CODES
    return False


def raise_for_retryable_response(response: httpx.Response) -> None:
    # Call this right after every API response.  It converts retryable status codes into
    # RetryableAPIError so tenacity's retry decorator can catch and retry them.
    if response.status_code in RETRYABLE_STATUS_CODES:
        raise RetryableAPIError(response.status_code, response.text)
    # For all other non-2xx codes, raise immediately without retrying.
    response.raise_for_status()


def api_retry():
    # Decorator factory — returns a tenacity @retry decorator configured from settings.
    # Usage: @api_retry() above any method that makes an HTTP call.
    settings = get_settings()
    return retry(
        retry=retry_if_exception(is_retryable),
        stop=stop_after_attempt(settings.max_retry_attempts),
        # Wait 2s, then 4s, then 8s … up to 30s between attempts.
        wait=wait_exponential(multiplier=1, min=2, max=30),
        # Log a WARNING before each sleep so we can see retries in the logs.
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,  # re-raise the last exception if all attempts are exhausted
    )
