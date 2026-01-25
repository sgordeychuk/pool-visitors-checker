from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.analytics import (
    WeekdayAverage, HeatmapData, DailySummary, TrendData, WeekdayAverageUpToNow
)
from app.services.analytics_service import AnalyticsService
from app.services.pool_service import PoolService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/weekday-averages", response_model=List[WeekdayAverage])
def get_weekday_averages(
    pool_id: int = Query(..., description="Pool ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get average visitor counts by weekday and hour for a pool."""
    # Verify pool exists
    pool_service = PoolService(db)
    if not pool_service.get_by_id(pool_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )

    analytics = AnalyticsService(db)
    return analytics.get_weekday_averages(pool_id)


@router.get("/heatmap", response_model=HeatmapData)
def get_heatmap_data(
    pool_id: int = Query(..., description="Pool ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get heatmap data (weekday x hour) for a pool."""
    analytics = AnalyticsService(db)
    data = analytics.get_heatmap_data(pool_id)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )

    return data


@router.get("/daily-summary", response_model=List[DailySummary])
def get_daily_summary(
    pool_id: int = Query(..., description="Pool ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily summary statistics for a pool."""
    # Verify pool exists
    pool_service = PoolService(db)
    if not pool_service.get_by_id(pool_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )

    analytics = AnalyticsService(db)
    return analytics.get_daily_summary(pool_id, start_date, end_date)


@router.get("/trends", response_model=TrendData)
def get_trends(
    pool_id: int = Query(..., description="Pool ID"),
    period: str = Query("weekly", description="Period type: 'weekly' or 'monthly'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trend analysis for a pool."""
    if period not in ["weekly", "monthly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period must be 'weekly' or 'monthly'"
        )

    analytics = AnalyticsService(db)
    data = analytics.get_trends(pool_id, period)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )

    return data


@router.get("/peak-hours")
def get_peak_hours(
    pool_id: int = Query(..., description="Pool ID"),
    weekday: Optional[str] = Query(None, description="Filter by weekday"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get peak hours analysis for a pool."""
    # Verify pool exists
    pool_service = PoolService(db)
    if not pool_service.get_by_id(pool_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )

    analytics = AnalyticsService(db)
    return analytics.get_peak_hours(pool_id, weekday)


@router.get("/weekday-average-now", response_model=WeekdayAverageUpToNow)
def get_weekday_average_up_to_now(
    pool_id: int = Query(..., description="Pool ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get average visitor count for current weekday up to current time of day."""
    analytics = AnalyticsService(db)
    data = analytics.get_weekday_average_up_to_now(pool_id)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )

    return data
