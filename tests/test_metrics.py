# Unit tests for the three core metric calculation functions.
# Covers both normal cases and the divide-by-zero edge cases.

from app.services.metrics_service import calculate_cpc, calculate_ctr, calculate_roas


def test_ctr_normal():
    # 100 clicks out of 10 000 impressions = 1 % CTR.
    assert calculate_ctr(100, 10_000) == 0.01


def test_ctr_zero_impressions():
    # No impressions means CTR is undefined — return 0 instead of raising ZeroDivisionError.
    assert calculate_ctr(100, 0) == 0.0


def test_cpc_normal():
    # $50 spend / 100 clicks = $0.50 per click.
    assert calculate_cpc(50, 100) == 0.5


def test_cpc_zero_clicks():
    # No clicks means CPC is undefined — return 0.
    assert calculate_cpc(50, 0) == 0.0


def test_roas_normal():
    # $500 revenue / $100 spend = 5× ROAS.
    assert calculate_roas(500, 100) == 5.0


def test_roas_zero_spend():
    # No spend means ROAS is undefined — return 0.
    assert calculate_roas(500, 0) == 0.0
