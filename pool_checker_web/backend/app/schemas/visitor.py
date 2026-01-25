from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List


class VisitorRecordBase(BaseModel):
    pool_id: int
    timestamp: datetime
    weekday: str
    visitor_count: int = Field(..., ge=0)
    week_number: Optional[int] = None


class VisitorRecordCreate(VisitorRecordBase):
    pass


class VisitorRecordResponse(VisitorRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class VisitorRecordFilter(BaseModel):
    pool_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    weekday: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=10000)
    offset: int = Field(default=0, ge=0)


class LatestVisitorResponse(BaseModel):
    pool_id: int
    pool_name: str
    visitor_count: int
    timestamp: datetime
    weekday: str


class PaginatedVisitorResponse(BaseModel):
    records: List[VisitorRecordResponse]
    total: int
    limit: int
    offset: int
    has_more: bool
