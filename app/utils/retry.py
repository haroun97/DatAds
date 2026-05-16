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
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class RetryableAPIError(Exception):
    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        super().__init__(message or f"Retryable API error: {status_code}")


def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TimeoutException | httpx.NetworkError):
        return True
    if isinstance(exc, RetryableAPIError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS_CODES
    return False


def raise_for_retryable_response(response: httpx.Response) -> None:
    if response.status_code in RETRYABLE_STATUS_CODES:
        raise RetryableAPIError(response.status_code, response.text)
    response.raise_for_status()


def api_retry():
    settings = get_settings()
    return retry(
        retry=retry_if_exception(is_retryable),
        stop=stop_after_attempt(settings.max_retry_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
