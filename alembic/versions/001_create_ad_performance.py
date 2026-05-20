"""create ad performance table

Revision ID: 001
Revises:
Create Date: 2026-05-16

"""

# Initial migration — creates the ad_performance table with all columns and indexes.
# Run with: alembic upgrade head

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None   # first migration, no parent
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ad_performance",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("campaign_id", sa.String(length=255), nullable=False),
        sa.Column("ad_id", sa.String(length=255), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("spend", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("conversions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revenue", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("ctr", sa.Numeric(12, 6), nullable=False, server_default="0"),
        sa.Column("cpc", sa.Numeric(12, 6), nullable=False, server_default="0"),
        sa.Column("roas", sa.Numeric(12, 6), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        # Unique constraint prevents duplicate rows for the same ad on the same day.
        sa.UniqueConstraint("platform", "campaign_id", "ad_id", "date", name="uq_ad_performance"),
    )
    # Indexes on columns used in WHERE clauses and ORDER BY to keep queries fast.
    op.create_index("idx_ad_performance_platform", "ad_performance", ["platform"])
    op.create_index("idx_ad_performance_date", "ad_performance", ["date"])
    op.create_index("idx_ad_performance_campaign", "ad_performance", ["campaign_id"])
    op.create_index("idx_ad_performance_platform_date", "ad_performance", ["platform", "date"])
    op.create_index("idx_ad_performance_roas", "ad_performance", ["roas"])
    op.create_index("idx_ad_performance_ctr", "ad_performance", ["ctr"])
    op.create_index("idx_ad_performance_cpc", "ad_performance", ["cpc"])


def downgrade() -> None:
    # Drop indexes before the table (required by some DB engines).
    op.drop_index("idx_ad_performance_cpc", table_name="ad_performance")
    op.drop_index("idx_ad_performance_ctr", table_name="ad_performance")
    op.drop_index("idx_ad_performance_roas", table_name="ad_performance")
    op.drop_index("idx_ad_performance_platform_date", table_name="ad_performance")
    op.drop_index("idx_ad_performance_campaign", table_name="ad_performance")
    op.drop_index("idx_ad_performance_date", table_name="ad_performance")
    op.drop_index("idx_ad_performance_platform", table_name="ad_performance")
    op.drop_table("ad_performance")
