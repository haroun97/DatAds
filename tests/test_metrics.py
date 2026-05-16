from app.services.metrics_service import calculate_cpc, calculate_ctr, calculate_roas


def test_ctr_normal():
    assert calculate_ctr(100, 10_000) == 0.01


def test_ctr_zero_impressions():
    assert calculate_ctr(100, 0) == 0.0


def test_cpc_normal():
    assert calculate_cpc(50, 100) == 0.5


def test_cpc_zero_clicks():
    assert calculate_cpc(50, 0) == 0.0


def test_roas_normal():
    assert calculate_roas(500, 100) == 5.0


def test_roas_zero_spend():
    assert calculate_roas(500, 0) == 0.0
