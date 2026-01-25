from celery import Celery
from celery.schedules import crontab
import os

# Get Redis URL from environment
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "pool_checker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["celery_app.tasks.scraper_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="CET",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Celery Beat schedule
celery_app.conf.beat_schedule = {
    "scrape-all-pools-every-10-minutes": {
        "task": "celery_app.tasks.scraper_tasks.scrape_all_pools",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
    },
    "refresh-analytics-cache-daily": {
        "task": "celery_app.tasks.scraper_tasks.refresh_analytics_cache",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}
