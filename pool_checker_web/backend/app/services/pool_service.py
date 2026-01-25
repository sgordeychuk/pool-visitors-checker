from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.pool import Pool
from app.models.visitor import VisitorRecord
from app.schemas.pool import PoolCreate, PoolUpdate, PoolWithStats


class PoolService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Pool]:
        """Get all pools."""
        return self.db.query(Pool).offset(skip).limit(limit).all()

    def get_active(self) -> List[Pool]:
        """Get all active pools."""
        return self.db.query(Pool).filter(Pool.is_active == True).all()

    def get_by_id(self, pool_id: int) -> Optional[Pool]:
        """Get a pool by ID."""
        return self.db.query(Pool).filter(Pool.id == pool_id).first()

    def get_by_name(self, name: str) -> Optional[Pool]:
        """Get a pool by name."""
        return self.db.query(Pool).filter(Pool.name == name).first()

    def create(self, pool_in: PoolCreate) -> Pool:
        """Create a new pool."""
        pool = Pool(**pool_in.model_dump())
        self.db.add(pool)
        self.db.commit()
        self.db.refresh(pool)
        return pool

    def update(self, pool: Pool, pool_in: PoolUpdate) -> Pool:
        """Update a pool."""
        update_data = pool_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pool, field, value)

        self.db.commit()
        self.db.refresh(pool)
        return pool

    def delete(self, pool: Pool) -> None:
        """Delete a pool."""
        self.db.delete(pool)
        self.db.commit()

    def get_with_stats(self, pool_id: int) -> Optional[PoolWithStats]:
        """Get a pool with its latest stats."""
        pool = self.get_by_id(pool_id)
        if not pool:
            return None

        # Get latest visitor record
        latest_record = (
            self.db.query(VisitorRecord)
            .filter(VisitorRecord.pool_id == pool_id)
            .order_by(VisitorRecord.timestamp.desc())
            .first()
        )

        # Get total record count
        total_records = (
            self.db.query(func.count(VisitorRecord.id))
            .filter(VisitorRecord.pool_id == pool_id)
            .scalar()
        )

        return PoolWithStats(
            id=pool.id,
            name=pool.name,
            url=pool.url,
            element_id=pool.element_id,
            timezone=pool.timezone,
            scrape_start_time=pool.scrape_start_time,
            scrape_end_time=pool.scrape_end_time,
            scrape_interval_minutes=pool.scrape_interval_minutes,
            is_active=pool.is_active,
            created_at=pool.created_at,
            latest_visitor_count=latest_record.visitor_count if latest_record else None,
            latest_reading_time=latest_record.timestamp if latest_record else None,
            total_records=total_records or 0
        )

    def get_all_with_stats(self) -> List[PoolWithStats]:
        """Get all pools with their stats."""
        pools = self.get_all()
        result = []
        for pool in pools:
            stats = self.get_with_stats(pool.id)
            if stats:
                result.append(stats)
        return result
