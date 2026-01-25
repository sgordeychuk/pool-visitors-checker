from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.pool import PoolCreate, PoolUpdate, PoolResponse, PoolWithStats
from app.services.pool_service import PoolService
from app.services.visitor_service import VisitorService
from app.core.security import get_current_user, get_current_active_superuser
from app.models.user import User

router = APIRouter(prefix="/pools", tags=["Pools"])


@router.get("", response_model=List[PoolWithStats])
def list_pools(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pools with their stats."""
    service = PoolService(db)
    return service.get_all_with_stats()


@router.get("/{pool_id}", response_model=PoolWithStats)
def get_pool(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific pool with stats."""
    service = PoolService(db)
    pool = service.get_with_stats(pool_id)
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )
    return pool


@router.post("", response_model=PoolResponse, status_code=status.HTTP_201_CREATED)
def create_pool(
    pool_in: PoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """Create a new pool configuration (admin only)."""
    service = PoolService(db)

    # Check if name already exists
    if service.get_by_name(pool_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pool with this name already exists"
        )

    return service.create(pool_in)


@router.put("/{pool_id}", response_model=PoolResponse)
def update_pool(
    pool_id: int,
    pool_in: PoolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """Update a pool configuration (admin only)."""
    service = PoolService(db)
    pool = service.get_by_id(pool_id)
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )

    # Check for name conflict if name is being updated
    if pool_in.name and pool_in.name != pool.name:
        existing = service.get_by_name(pool_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pool with this name already exists"
            )

    return service.update(pool, pool_in)


@router.delete("/{pool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pool(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """Delete a pool and all its data (admin only)."""
    service = PoolService(db)
    pool = service.get_by_id(pool_id)
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )
    service.delete(pool)


@router.get("/{pool_id}/current")
def get_current_visitors(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current visitor count for a pool."""
    pool_service = PoolService(db)
    pool = pool_service.get_by_id(pool_id)
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )

    visitor_service = VisitorService(db)
    latest = visitor_service.get_latest_for_pool(pool_id)

    if not latest:
        return {
            "pool_id": pool_id,
            "pool_name": pool.name,
            "visitor_count": None,
            "timestamp": None,
            "message": "No visitor data available"
        }

    return {
        "pool_id": pool_id,
        "pool_name": pool.name,
        "visitor_count": latest.visitor_count,
        "timestamp": latest.timestamp,
        "weekday": latest.weekday
    }


@router.post("/{pool_id}/scrape", status_code=status.HTTP_202_ACCEPTED)
def trigger_scrape(
    pool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """Trigger a manual scrape for a pool (admin only)."""
    service = PoolService(db)
    pool = service.get_by_id(pool_id)
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pool not found"
        )

    # Import and trigger the Celery task
    from celery_app.tasks.scraper_tasks import scrape_pool
    task = scrape_pool.delay(pool_id)

    return {
        "message": "Scrape task queued",
        "task_id": task.id,
        "pool_id": pool_id
    }
