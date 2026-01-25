from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Pool(Base):
    __tablename__ = "pools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    element_id = Column(String(100), nullable=False)
    timezone = Column(String(50), default="CET")
    scrape_start_time = Column(String(5), default="05:50")
    scrape_end_time = Column(String(5), default="22:10")
    scrape_interval_minutes = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to visitor records
    visitor_records = relationship(
        "VisitorRecord",
        back_populates="pool",
        cascade="all, delete-orphan"
    )
