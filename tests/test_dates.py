from datetime import date

from app.utils.dates import last_n_days


def test_last_n_days_window_is_inclusive():
    """last_n_days(30) returns exactly 30 days including the end date."""
    since, until = last_n_days(30, end=date(2026, 5, 19))
    assert until == date(2026, 5, 19)
    assert since == date(2026, 4, 20)
    assert (until - since).days == 29  # 30 days inclusive = difference of 29


def test_last_n_days_single_day():
    since, until = last_n_days(1, end=date(2026, 5, 19))
    assert since == until == date(2026, 5, 19)


def test_last_n_days_defaults_to_today():
    since, until = last_n_days(30)
    assert until == date.today()
    assert (until - since).days == 29
