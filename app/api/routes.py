# API route handlers for the analytics endpoints.
# All routes live under the /api prefix and are documented in Swagger at /docs.

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.ad_performance import MetricName, PerformanceFilters, SortOrder
from app.schemas.api_responses import PerformanceResponse, TopPerformingResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api", tags=["Analytics"])

# Only these metric names are accepted by /top-performing.
ALLOWED_METRICS: set[str] = {"ctr", "cpc", "roas", "clicks", "revenue"}

# Shared query parameters (brief descriptions + examples for Swagger /docs)
PlatformQuery = Query(None, description="Platform filter, e.g. `facebook`.", examples=["facebook"])

DateFromQuery = Query(
    None,
    alias="date_from",
    description="Start date (`YYYY-MM-DD`).",
    examples=["2026-04-19"],
)

DateToQuery = Query(
    None,
    alias="date_to",
    description="End date (`YYYY-MM-DD`).",
    examples=["2026-05-18"],
)

CampaignIdQuery = Query(
    None,
    description="Campaign ID, e.g. `fb_camp_123`.",
    examples=["fb_camp_123"],
)

MetricQuery = Query(
    ...,
    description="Sort metric: `ctr`, `cpc`, `roas`, `clicks`, `revenue`.",
    examples=["roas"],
)

OrderQuery = Query("desc", description="`asc` or `desc` (default).", examples=["desc"])

LimitQuery = Query(10, ge=1, le=100, description="Max rows (1–100).", examples=[5])


def _parse_filters(
    platform: str | None,
    date_from: date | None,
    date_to: date | None,
    campaign_id: str | None,
) -> PerformanceFilters:
    # Guard against impossible date ranges before hitting the database.
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=400,
            detail="date_from must be on or before date_to",
        )
    return PerformanceFilters(
        platform=platform,
        date_from=date_from,
        date_to=date_to,
        campaign_id=campaign_id,
    )


def _filters_applied(filters: PerformanceFilters) -> dict[str, str | None]:
    # Serialize the active filters into the API response so callers know what was applied.
    return {
        "platform": filters.platform,
        "date_from": filters.date_from.isoformat() if filters.date_from else None,
        "date_to": filters.date_to.isoformat() if filters.date_to else None,
        "campaign_id": filters.campaign_id,
    }


@router.get(
    "/performance",
    response_model=PerformanceResponse,
    summary="Aggregated performance metrics",
    description="Totals and average CTR, CPC, ROAS for matching ads. All params optional.",
)
def get_performance(
    platform: str | None = PlatformQuery,
    date_from: date | None = DateFromQuery,
    date_to: date | None = DateToQuery,
    campaign_id: str | None = CampaignIdQuery,
    db: Session = Depends(get_db),
) -> PerformanceResponse:
    filters = _parse_filters(platform, date_from, date_to, campaign_id)
    data = AnalyticsService(db).get_aggregated_performance(filters)
    return PerformanceResponse(data=data, filters_applied=_filters_applied(filters))


@router.get(
    "/top-performing",
    response_model=TopPerformingResponse,
    summary="Top-performing ads by metric",
    description=(
        "Returns the best ads sorted by `metric` (e.g. roas). "
        "Response `data`: up to `limit` ads only (example: 5 rows). "
        "Response `pagination.total`: all ads that match your filters (example: 87), "
        "even if you only asked for 5."
    ),
)
def get_top_performing(
    metric: str = MetricQuery,
    order: SortOrder = OrderQuery,
    limit: int = LimitQuery,
    platform: str | None = PlatformQuery,
    date_from: date | None = DateFromQuery,
    date_to: date | None = DateToQuery,
    db: Session = Depends(get_db),
) -> TopPerformingResponse:
    # Reject unknown metric names early with a clear error message.
    if metric not in ALLOWED_METRICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Allowed values: {', '.join(sorted(ALLOWED_METRICS))}",
        )

    filters = _parse_filters(platform, date_from, date_to, campaign_id=None)
    records, total = AnalyticsService(db).get_top_performing(
        filters=filters,
        metric=metric,  # type: ignore[arg-type]
        order=order,
        limit=limit,
    )
    return TopPerformingResponse(
        data=records,
        # `total` is the full match count; `limit` is how many rows were returned.
        pagination={"limit": limit, "total": total},
    )
