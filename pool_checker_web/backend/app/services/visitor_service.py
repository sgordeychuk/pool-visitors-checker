from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.visitor import VisitorRecord
from app.models.pool import Pool
from app.schemas.visitor import (
    VisitorRecordCreate, VisitorRecordFilter, LatestVisitorResponse, PaginatedVisitorResponse,
    VisitorRecordResponse
)


class VisitorService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, record_in: VisitorRecordCreate) -> VisitorRecord:
        """Create a new visitor record."""
        record = VisitorRecord(**record_in.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def create_from_scrape(
        self,
        pool_id: int,
        visitor_count: int,
        timestamp: datetime
    ) -> VisitorRecord:
        """Create a visitor record from a scrape result."""
        weekday = timestamp.strftime('%A')
        week_number = timestamp.isocalendar()[1]

        record = VisitorRecord(
            pool_id=pool_id,
            timestamp=timestamp,
            weekday=weekday,
            visitor_count=visitor_count,
            week_number=week_number
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, record_id: int) -> Optional[VisitorRecord]:
        """Get a visitor record by ID."""
        return self.db.query(VisitorRecord).filter(VisitorRecord.id == record_id).first()

    def get_filtered(self, filters: VisitorRecordFilter) -> List[VisitorRecord]:
        """Get visitor records with filters."""
        query = self.db.query(VisitorRecord)

        if filters.pool_id:
            query = query.filter(VisitorRecord.pool_id == filters.pool_id)

        if filters.start_date:
            start_dt = datetime.combine(filters.start_date, datetime.min.time())
            query = query.filter(VisitorRecord.timestamp >= start_dt)

        if filters.end_date:
            end_dt = datetime.combine(filters.end_date, datetime.max.time())
            query = query.filter(VisitorRecord.timestamp <= end_dt)

        if filters.weekday:
            query = query.filter(VisitorRecord.weekday == filters.weekday)

        return (
            query
            .order_by(VisitorRecord.timestamp.desc())
            .offset(filters.offset)
            .limit(filters.limit)
            .all()
        )

    def get_latest_for_pool(self, pool_id: int) -> Optional[VisitorRecord]:
        """Get the latest visitor record for a pool."""
        return (
            self.db.query(VisitorRecord)
            .filter(VisitorRecord.pool_id == pool_id)
            .order_by(VisitorRecord.timestamp.desc())
            .first()
        )

    def get_latest_all_pools(self) -> List[LatestVisitorResponse]:
        """Get the latest visitor count for all pools."""
        # Subquery to get the latest timestamp for each pool
        subquery = (
            self.db.query(
                VisitorRecord.pool_id,
                func.max(VisitorRecord.timestamp).label('max_timestamp')
            )
            .group_by(VisitorRecord.pool_id)
            .subquery()
        )

        # Join to get the full record
        results = (
            self.db.query(VisitorRecord, Pool)
            .join(Pool, VisitorRecord.pool_id == Pool.id)
            .join(
                subquery,
                and_(
                    VisitorRecord.pool_id == subquery.c.pool_id,
                    VisitorRecord.timestamp == subquery.c.max_timestamp
                )
            )
            .all()
        )

        return [
            LatestVisitorResponse(
                pool_id=record.pool_id,
                pool_name=pool.name,
                visitor_count=record.visitor_count,
                timestamp=record.timestamp,
                weekday=record.weekday
            )
            for record, pool in results
        ]

    def get_today_for_pool(self, pool_id: int) -> List[VisitorRecord]:
        """Get all visitor records for today for a specific pool."""
        today = date.today()
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())

        return (
            self.db.query(VisitorRecord)
            .filter(
                VisitorRecord.pool_id == pool_id,
                VisitorRecord.timestamp >= start_dt,
                VisitorRecord.timestamp <= end_dt
            )
            .order_by(VisitorRecord.timestamp.asc())
            .all()
        )

    def count_records(self, pool_id: Optional[int] = None) -> int:
        """Count total visitor records."""
        query = self.db.query(func.count(VisitorRecord.id))
        if pool_id:
            query = query.filter(VisitorRecord.pool_id == pool_id)
        return query.scalar() or 0

    def check_duplicate(self, pool_id: int, timestamp: datetime) -> bool:
        """Check if a record with the same pool and timestamp already exists."""
        existing = (
            self.db.query(VisitorRecord)
            .filter(
                VisitorRecord.pool_id == pool_id,
                VisitorRecord.timestamp == timestamp
            )
            .first()
        )
        return existing is not None

    def get_paginated(self, filters: VisitorRecordFilter) -> PaginatedVisitorResponse:
        """Get visitor records with pagination info."""
        query = self.db.query(VisitorRecord)

        if filters.pool_id:
            query = query.filter(VisitorRecord.pool_id == filters.pool_id)

        if filters.start_date:
            start_dt = datetime.combine(filters.start_date, datetime.min.time())
            query = query.filter(VisitorRecord.timestamp >= start_dt)

        if filters.end_date:
            end_dt = datetime.combine(filters.end_date, datetime.max.time())
            query = query.filter(VisitorRecord.timestamp <= end_dt)

        if filters.weekday:
            query = query.filter(VisitorRecord.weekday == filters.weekday)

        # Get total count
        total = query.count()

        # Get records with pagination
        records = (
            query
            .order_by(VisitorRecord.timestamp.desc())
            .offset(filters.offset)
            .limit(filters.limit)
            .all()
        )

        return PaginatedVisitorResponse(
            records=[VisitorRecordResponse.model_validate(r) for r in records],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
            has_more=(filters.offset + len(records)) < total
        )
