# Date-range helpers used when scheduling ingestion jobs.

from datetime import date, timedelta


def last_n_days(n: int = 30, end: date | None = None) -> tuple[date, date]:
    # Returns (start, end) for an inclusive window of exactly n days.
    # Example: last_n_days(30) on May 19 returns (Apr 20, May 19).
    end_date = end or date.today()
    start_date = end_date - timedelta(days=n - 1)
    return start_date, end_date
