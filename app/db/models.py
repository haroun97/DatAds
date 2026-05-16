import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Index, Integer, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AdPerformance(Base):
    __tablename__ = "ad_performance"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    campaign_id: Mapped[str] = mapped_column(String(255), nullable=False)
    ad_id: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    spend: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    conversions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    ctr: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, default=0)
    cpc: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, default=0)
    roas: Mapped[float] = mapped_column(Numeric(12, 6), nullable=False, default=0)

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
        UniqueConstraint("platform", "campaign_id", "ad_id", "date", name="uq_ad_performance"),
        Index("idx_ad_performance_platform", "platform"),
        Index("idx_ad_performance_date", "date"),
        Index("idx_ad_performance_campaign", "campaign_id"),
        Index("idx_ad_performance_platform_date", "platform", "date"),
        Index("idx_ad_performance_roas", "roas"),
        Index("idx_ad_performance_ctr", "ctr"),
        Index("idx_ad_performance_cpc", "cpc"),
    )
