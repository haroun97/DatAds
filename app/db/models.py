# SQLAlchemy ORM model for the ad_performance table.
# One row = one ad's metrics for one day on one platform.

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Index, Integer, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AdPerformance(Base):
    __tablename__ = "ad_performance"

    # UUID primary key avoids sequential ID leakage and works across distributed inserts.
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Identity columns — together with `date` they form the unique key for upserts.
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    campaign_id: Mapped[str] = mapped_column(String(255), nullable=False)
    ad_id: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # Raw counts from the ad platform.
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    spend: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    conversions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    # Derived metrics stored alongside raw data to avoid recomputing on every read.
    ctr: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, default=0)
    cpc: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, default=0)
    roas: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, default=0)

    # Audit timestamps — updated_at is refreshed automatically on every UPDATE.
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        # Prevents duplicate rows for the same ad/day; also used as the upsert conflict target.
        UniqueConstraint("platform", "campaign_id", "ad_id", "date", name="uq_ad_performance"),
        # Indexes on common filter and sort columns to keep API queries fast.
        Index("idx_ad_performance_platform", "platform"),
        Index("idx_ad_performance_date", "date"),
        Index("idx_ad_performance_campaign", "campaign_id"),
        Index("idx_ad_performance_platform_date", "platform", "date"),
        Index("idx_ad_performance_roas", "roas"),
        Index("idx_ad_performance_ctr", "ctr"),
        Index("idx_ad_performance_cpc", "cpc"),
    )
