import os
import time
from datetime import datetime, time as dt_time
from typing import Optional

import pytz
from celery import shared_task
from celery.utils.log import get_task_logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.pool import Pool
from app.models.visitor import VisitorRecord
from app.services.visitor_service import VisitorService
from app.services.pool_service import PoolService

logger = get_task_logger(__name__)


def get_db_session() -> Session:
    """Get a database session for use in Celery tasks."""
    return SessionLocal()


def is_within_active_hours(pool: Pool) -> bool:
    """Check if current time is within the pool's active hours."""
    tz = pytz.timezone(pool.timezone)
    now = datetime.now(tz)
    current_time = now.time()

    start_parts = pool.scrape_start_time.split(":")
    end_parts = pool.scrape_end_time.split(":")

    start_time = dt_time(int(start_parts[0]), int(start_parts[1]))
    end_time = dt_time(int(end_parts[0]), int(end_parts[1]))

    return start_time <= current_time <= end_time


def fetch_visitor_count(url: str, element_id: str) -> Optional[int]:
    """Fetch the visitor count from a webpage using Selenium."""
    driver = None
    try:
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Use chromium binary from environment if set
        chrome_bin = os.environ.get("CHROME_BIN")
        if chrome_bin:
            chrome_options.binary_location = chrome_bin

        # Create the driver using system chromedriver or env path
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Load the page
        driver.get(url)

        # Wait for JavaScript to execute
        time.sleep(10)

        # Find the element with the visitor number
        element = driver.find_element(By.ID, element_id)

        if element:
            visitor_text = element.text.strip()
            # Parse the visitor count (handle potential non-numeric characters)
            visitor_count = int("".join(filter(str.isdigit, visitor_text)))
            return visitor_count
        else:
            logger.error(f"Element with ID '{element_id}' not found")
            return None

    except Exception as e:
        logger.error(f"Error fetching visitor count: {e}")
        return None
    finally:
        if driver:
            driver.quit()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="celery_app.tasks.scraper_tasks.scrape_pool"
)
def scrape_pool(self, pool_id: int) -> dict:
    """Scrape visitor count for a single pool."""
    db = get_db_session()
    try:
        pool_service = PoolService(db)
        pool = pool_service.get_by_id(pool_id)

        if not pool:
            logger.error(f"Pool {pool_id} not found")
            return {"success": False, "error": "Pool not found"}

        if not pool.is_active:
            logger.info(f"Pool {pool_id} is not active, skipping")
            return {"success": False, "error": "Pool is not active"}

        if not is_within_active_hours(pool):
            logger.info(f"Pool {pool_id} is outside active hours, skipping")
            return {"success": False, "error": "Outside active hours"}

        # Fetch the visitor count
        visitor_count = fetch_visitor_count(pool.url, pool.element_id)

        if visitor_count is None:
            logger.error(f"Failed to fetch visitor count for pool {pool_id}")
            return {"success": False, "error": "Failed to fetch visitor count"}

        # Get current timestamp in pool's timezone
        tz = pytz.timezone(pool.timezone)
        timestamp = datetime.now(tz)

        # Create the visitor record
        visitor_service = VisitorService(db)
        record = visitor_service.create_from_scrape(
            pool_id=pool_id,
            visitor_count=visitor_count,
            timestamp=timestamp
        )

        logger.info(
            f"Scraped pool {pool_id} ({pool.name}): "
            f"{visitor_count} visitors at {timestamp}"
        )

        return {
            "success": True,
            "pool_id": pool_id,
            "pool_name": pool.name,
            "visitor_count": visitor_count,
            "timestamp": timestamp.isoformat(),
            "record_id": record.id
        }

    except Exception as e:
        logger.error(f"Error scraping pool {pool_id}: {e}")
        raise
    finally:
        db.close()


@shared_task(name="celery_app.tasks.scraper_tasks.scrape_all_pools")
def scrape_all_pools() -> dict:
    """Scrape visitor counts for all active pools."""
    db = get_db_session()
    try:
        pool_service = PoolService(db)
        active_pools = pool_service.get_active()

        if not active_pools:
            logger.info("No active pools to scrape")
            return {"success": True, "pools_scraped": 0}

        results = []
        for pool in active_pools:
            # Trigger individual scrape task for each pool
            task = scrape_pool.delay(pool.id)
            results.append({
                "pool_id": pool.id,
                "pool_name": pool.name,
                "task_id": task.id
            })

        logger.info(f"Triggered scraping for {len(results)} pools")
        return {
            "success": True,
            "pools_scraped": len(results),
            "tasks": results
        }

    except Exception as e:
        logger.error(f"Error in scrape_all_pools: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@shared_task(name="celery_app.tasks.scraper_tasks.refresh_analytics_cache")
def refresh_analytics_cache() -> dict:
    """Refresh pre-computed analytics cache (placeholder for future optimization)."""
    logger.info("Refreshing analytics cache...")
    # This is a placeholder for future caching implementation
    # Could pre-compute weekday averages, heatmap data, etc.
    return {"success": True, "message": "Analytics cache refreshed"}
