# Tests for the last_n_days date helper.

from datetime import date

from app.utils.dates import last_n_days


def test_last_n_days_window_is_inclusive():
    """last_n_days(30) returns exactly 30 days including the end date."""
    since, until = last_n_days(30, end=date(2026, 5, 19))
    assert until == date(2026, 5, 19)
    assert since == date(2026, 4, 20)
    # 30 inclusive days = difference of 29 days between start and end.
    assert (until - since).days == 29


def test_last_n_days_single_day():
    # A window of 1 day means start and end are the same date.
    since, until = last_n_days(1, end=date(2026, 5, 19))
    assert since == until == date(2026, 5, 19)


def test_last_n_days_defaults_to_today():
    # When no end date is given, the window ends today.
    since, until = last_n_days(30)
    assert until == date.today()
    assert (until - since).days == 29
