from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class VisitorRecord(Base):
    __tablename__ = "visitor_records"

    id = Column(Integer, primary_key=True, index=True)
    pool_id = Column(Integer, ForeignKey("pools.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    weekday = Column(String(10), nullable=False)
    visitor_count = Column(Integer, nullable=False)
    week_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to pool
    pool = relationship("Pool", back_populates="visitor_records")

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_visitor_pool_timestamp", "pool_id", "timestamp"),
        Index("ix_visitor_pool_weekday", "pool_id", "weekday"),
    )
