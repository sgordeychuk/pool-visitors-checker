from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.visitor import (
    VisitorRecordResponse, VisitorRecordFilter, LatestVisitorResponse, PaginatedVisitorResponse
)
from app.services.visitor_service import VisitorService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/visitors", tags=["Visitors"])


@router.get("", response_model=List[VisitorRecordResponse])
def list_visitors(
    pool_id: Optional[int] = Query(None, description="Filter by pool ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    weekday: Optional[str] = Query(None, description="Filter by weekday (e.g., Monday)"),
    limit: int = Query(100, ge=1, le=10000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get visitor records with filters."""
    service = VisitorService(db)
    filters = VisitorRecordFilter(
        pool_id=pool_id,
        start_date=start_date,
        end_date=end_date,
        weekday=weekday,
        limit=limit,
        offset=offset
    )
    return service.get_filtered(filters)


@router.get("/latest", response_model=List[LatestVisitorResponse])
def get_latest_visitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest visitor readings for all pools."""
    service = VisitorService(db)
    return service.get_latest_all_pools()


@router.get("/today/{pool_id}", response_model=List[VisitorRecordResponse])
def get_today_visitors(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all visitor records for today for a specific pool."""
    service = VisitorService(db)
    return service.get_today_for_pool(pool_id)


@router.get("/count")
def get_visitor_count(
    pool_id: Optional[int] = Query(None, description="Filter by pool ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the total count of visitor records."""
    service = VisitorService(db)
    count = service.count_records(pool_id)
    return {"count": count, "pool_id": pool_id}


@router.get("/paginated", response_model=PaginatedVisitorResponse)
def get_visitors_paginated(
    pool_id: Optional[int] = Query(None, description="Filter by pool ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    weekday: Optional[str] = Query(None, description="Filter by weekday (e.g., Monday)"),
    limit: int = Query(50, ge=1, le=1000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get visitor records with pagination info (for raw data view)."""
    service = VisitorService(db)
    filters = VisitorRecordFilter(
        pool_id=pool_id,
        start_date=start_date,
        end_date=end_date,
        weekday=weekday,
        limit=limit,
        offset=offset
    )
    return service.get_paginated(filters)
