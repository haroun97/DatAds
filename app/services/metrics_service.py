# Pure functions for computing the three core ad performance metrics.
# All division-by-zero cases return 0.0 so callers never have to guard against them.


def calculate_ctr(clicks: int, impressions: int) -> float:
    # Click-through rate: what fraction of people who saw the ad actually clicked it.
    if impressions == 0:
        return 0.0
    return clicks / impressions


def calculate_cpc(spend: float, clicks: int) -> float:
    # Cost per click: how much was spent on average to get one click.
    if clicks == 0:
        return 0.0
    return spend / clicks


def calculate_roas(revenue: float, spend: float) -> float:
    # Return on ad spend: how many dollars of revenue were earned per dollar spent.
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
    # Convenience wrapper — computes all three metrics at once and returns them as a dict
    # so they can be unpacked directly into AdPerformanceCreate(**metrics).
    return {
        "ctr": round(calculate_ctr(clicks, impressions), 6),
        "cpc": round(calculate_cpc(spend, clicks), 6),
        "roas": round(calculate_roas(revenue, spend), 6),
    }
