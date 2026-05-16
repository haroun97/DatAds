from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.ad_performance import MetricName, PerformanceFilters, SortOrder
from app.schemas.api_responses import PerformanceResponse, TopPerformingResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api")

ALLOWED_METRICS: set[str] = {"ctr", "cpc", "roas", "clicks", "revenue"}
ALLOWED_ORDERS: set[str] = {"asc", "desc"}


def _parse_filters(
    platform: str | None,
    date_from: date | None,
    date_to: date | None,
    campaign_id: str | None,
) -> PerformanceFilters:
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
    return {
        "platform": filters.platform,
        "date_from": filters.date_from.isoformat() if filters.date_from else None,
        "date_to": filters.date_to.isoformat() if filters.date_to else None,
        "campaign_id": filters.campaign_id,
    }


@router.get("/performance", response_model=PerformanceResponse)
def get_performance(
    platform: str | None = Query(None),
    date_from: date | None = Query(None, alias="date_from"),
    date_to: date | None = Query(None, alias="date_to"),
    campaign_id: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PerformanceResponse:
    filters = _parse_filters(platform, date_from, date_to, campaign_id)
    data = AnalyticsService(db).get_aggregated_performance(filters)
    return PerformanceResponse(data=data, filters_applied=_filters_applied(filters))


@router.get("/top-performing", response_model=TopPerformingResponse)
def get_top_performing(
    metric: str = Query(...),
    order: SortOrder = Query("desc"),
    limit: int = Query(10, ge=1, le=100),
    platform: str | None = Query(None),
    date_from: date | None = Query(None, alias="date_from"),
    date_to: date | None = Query(None, alias="date_to"),
    db: Session = Depends(get_db),
) -> TopPerformingResponse:
    if metric not in ALLOWED_METRICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Allowed values: {', '.join(sorted(ALLOWED_METRICS))}",
        )
    if order not in ALLOWED_ORDERS:
        raise HTTPException(
            status_code=400,
            detail="Invalid order. Allowed values: asc, desc",
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
        pagination={"limit": limit, "total": total},
    )
