#!/usr/bin/env python3
"""Ingest Facebook ad performance data for the last 30 days."""

# Manual ingestion script — run this directly to seed the database from the Facebook API.
# Usage: python scripts/ingest_facebook.py

import sys
from pathlib import Path

# Make the project root importable when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.logging import setup_logging
from app.db.database import SessionLocal
from app.db.repositories import AdPerformanceRepository
from app.pollers.facebook import FACEBOOK_CAMPAIGNS, FacebookPoller
from app.utils.dates import last_n_days


def main() -> None:
    setup_logging()
    since, until = last_n_days(30)
    print("Starting Facebook ingestion...")
    print(f"Date range: {since} to {until}\n")

    poller = FacebookPoller()
    db = SessionLocal()
    repo = AdPerformanceRepository(db)
    total_fetched = 0
    total_inserted = 0
    total_updated = 0

    try:
        for campaign_id in FACEBOOK_CAMPAIGNS:
            records = poller.fetch_campaign(campaign_id, since, until)
            inserted, updated = repo.upsert_many(records)
            total_fetched += len(records)
            total_inserted += inserted
            total_updated += updated
            print(f"Campaign {campaign_id}:")
            print(f"  Fetched {len(records)} records")
            print(f"  Inserted {inserted} records")
            print(f"  Updated {updated} records")
            if records:
                r = records[0]
                print(f"  Sample metrics — CTR: {r.ctr:.4f}, CPC: {r.cpc:.4f}, ROAS: {r.roas:.4f}")
            print()
    finally:
        # Always close the HTTP client and DB session, even if an error occurred.
        poller.close()
        db.close()

    print("Done.")
    print(f"Total fetched: {total_fetched}")
    print(f"Total inserted: {total_inserted}")
    print(f"Total updated: {total_updated}")


if __name__ == "__main__":
    main()
