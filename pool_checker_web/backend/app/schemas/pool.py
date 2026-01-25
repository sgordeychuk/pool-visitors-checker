from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional


class PoolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1)
    element_id: str = Field(..., min_length=1, max_length=100)
    timezone: str = Field(default="CET", max_length=50)
    scrape_start_time: str = Field(default="05:50", pattern=r"^\d{2}:\d{2}$")
    scrape_end_time: str = Field(default="22:10", pattern=r"^\d{2}:\d{2}$")
    scrape_interval_minutes: int = Field(default=10, ge=1, le=60)
    is_active: bool = True


class PoolCreate(PoolBase):
    pass


class PoolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = Field(None, min_length=1)
    element_id: Optional[str] = Field(None, min_length=1, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    scrape_start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    scrape_end_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    scrape_interval_minutes: Optional[int] = Field(None, ge=1, le=60)
    is_active: Optional[bool] = None


class PoolResponse(PoolBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PoolWithStats(PoolResponse):
    latest_visitor_count: Optional[int] = None
    latest_reading_time: Optional[datetime] = None
    total_records: int = 0
