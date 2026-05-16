def calculate_ctr(clicks: int, impressions: int) -> float:
    if impressions == 0:
        return 0.0
    return clicks / impressions


def calculate_cpc(spend: float, clicks: int) -> float:
    if clicks == 0:
        return 0.0
    return spend / clicks


def calculate_roas(revenue: float, spend: float) -> float:
    if spend == 0:
        return 0.0
    return revenue / spend


def enrich_metrics(
    *,
    impressions: int,
    clicks: int,
    spend: float,
    revenue: float,
) -> dict[str, float]:
    return {
        "ctr": round(calculate_ctr(clicks, impressions), 6),
        "cpc": round(calculate_cpc(spend, clicks), 6),
        "roas": round(calculate_roas(revenue, spend), 6),
    }
