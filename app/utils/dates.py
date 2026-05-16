from datetime import date, timedelta


def last_n_days(n: int = 30, end: date | None = None) -> tuple[date, date]:
    end_date = end or date.today()
    start_date = end_date - timedelta(days=n - 1)
    return start_date, end_date
