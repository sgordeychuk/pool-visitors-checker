#!/usr/bin/env python3
"""Script to import historical CSV data."""
import sys
import os
import csv
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytz
from app.db.database import SessionLocal
from app.models.pool import Pool
from app.models.visitor import VisitorRecord


def import_csv(csv_path: str, pool_id: int, batch_size: int = 500):
    """Import visitor data from CSV file."""
    db = SessionLocal()
    try:
        # Verify pool exists
        pool = db.query(Pool).filter(Pool.id == pool_id).first()
        if not pool:
            print(f"Error: Pool with ID {pool_id} not found")
            return

        print(f"Importing data for pool: {pool.name}")
        print(f"CSV file: {csv_path}")

        # Read CSV file
        with open(csv_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)

            records_added = 0
            records_skipped = 0
            batch = []

            for row in reader:
                # Parse timestamp - handle different formats
                timestamp_str = row.get("Timestamp") or row.get("timestamp")
                weekday = row.get("Weekday") or row.get("weekday")
                visitors_str = row.get("Visitors") or row.get("visitor_number") or row.get("visitors")

                if not all([timestamp_str, weekday, visitors_str]):
                    print(f"Skipping row with missing data: {row}")
                    records_skipped += 1
                    continue

                try:
                    # Parse timestamp
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    # Add timezone
                    tz = pytz.timezone(pool.timezone)
                    timestamp = tz.localize(timestamp)

                    # Parse visitor count
                    visitor_count = int(visitors_str)

                    # Check for duplicate
                    existing = db.query(VisitorRecord).filter(
                        VisitorRecord.pool_id == pool_id,
                        VisitorRecord.timestamp == timestamp
                    ).first()

                    if existing:
                        records_skipped += 1
                        continue

                    # Create record
                    record = VisitorRecord(
                        pool_id=pool_id,
                        timestamp=timestamp,
                        weekday=weekday,
                        visitor_count=visitor_count,
                        week_number=timestamp.isocalendar()[1]
                    )
                    batch.append(record)
                    records_added += 1

                    # Commit in batches
                    if len(batch) >= batch_size:
                        db.bulk_save_objects(batch)
                        db.commit()
                        print(f"  Committed batch of {len(batch)} records...")
                        batch = []

                except ValueError as e:
                    print(f"Error parsing row {row}: {e}")
                    records_skipped += 1
                    continue

            # Commit remaining records
            if batch:
                db.bulk_save_objects(batch)
                db.commit()
                print(f"  Committed final batch of {len(batch)} records...")

        print(f"\nImport complete:")
        print(f"  Records added: {records_added}")
        print(f"  Records skipped: {records_skipped}")

        # Verify total count
        total = db.query(VisitorRecord).filter(VisitorRecord.pool_id == pool_id).count()
        print(f"  Total records for pool: {total}")

    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_path}")
    except Exception as e:
        print(f"Error during import: {e}")
        db.rollback()
    finally:
        db.close()


def create_default_pool():
    """Create the default City Hallenbad pool if it doesn't exist."""
    db = SessionLocal()
    try:
        existing = db.query(Pool).filter(Pool.name == "City Hallenbad").first()
        if existing:
            print(f"Pool 'City Hallenbad' already exists with ID: {existing.id}")
            return existing.id

        pool = Pool(
            name="City Hallenbad",
            url="https://www.stadt-zuerich.ch/de/stadtleben/sport-und-erholung/sport-und-badeanlagen/hallenbaeder/city.html",
            element_id="SSD-4_visitornumber",
            timezone="CET",
            scrape_start_time="05:50",
            scrape_end_time="22:10",
            scrape_interval_minutes=10,
            is_active=True
        )
        db.add(pool)
        db.commit()
        db.refresh(pool)
        print(f"Created pool 'City Hallenbad' with ID: {pool.id}")
        return pool.id

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import visitor data from CSV")
    parser.add_argument(
        "--csv",
        type=str,
        default="/data/pool_data.csv",
        help="Path to CSV file (default: /data/pool_data.csv for Docker)"
    )
    parser.add_argument(
        "--pool-id",
        type=int,
        default=None,
        help="Pool ID to import data for (will create default pool if not specified)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of records to commit at a time"
    )

    args = parser.parse_args()

    # Create default pool if no pool ID specified
    if args.pool_id is None:
        args.pool_id = create_default_pool()

    import_csv(args.csv, args.pool_id, args.batch_size)
