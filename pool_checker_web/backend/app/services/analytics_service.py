from typing import List, Optional
from datetime import date, datetime, time
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, String
import pytz

from app.models.visitor import VisitorRecord
from app.models.pool import Pool
from app.schemas.analytics import (
    WeekdayAverage, HeatmapData, HeatmapCell,
    DailySummary, TrendData, TrendDataPoint, WeekdayAverageUpToNow
)


class AnalyticsService:
    # Pool opens at 6 AM - filter out earlier hours from all analytics
    POOL_OPEN_HOUR = 6
    POOL_CLOSE_HOUR = 22

    def __init__(self, db: Session):
        self.db = db

    def get_weekday_averages(self, pool_id: int) -> List[WeekdayAverage]:
        """Get average visitor counts by weekday and hour (during pool hours only)."""
        results = (
            self.db.query(
                VisitorRecord.weekday,
                extract('hour', VisitorRecord.timestamp).label('hour'),
                func.avg(VisitorRecord.visitor_count).label('avg_visitors'),
                func.count(VisitorRecord.id).label('sample_count')
            )
            .filter(
                VisitorRecord.pool_id == pool_id,
                extract('hour', VisitorRecord.timestamp) >= self.POOL_OPEN_HOUR,
                extract('hour', VisitorRecord.timestamp) <= self.POOL_CLOSE_HOUR
            )
            .group_by(VisitorRecord.weekday, extract('hour', VisitorRecord.timestamp))
            .order_by(VisitorRecord.weekday, 'hour')
            .all()
        )

        return [
            WeekdayAverage(
                weekday=row.weekday,
                hour=int(row.hour),
                average_visitors=round(float(row.avg_visitors), 1),
                sample_count=row.sample_count
            )
            for row in results
        ]

    def get_heatmap_data(self, pool_id: int) -> Optional[HeatmapData]:
        """Get heatmap data (weekday x hour matrix) during pool hours only."""
        pool = self.db.query(Pool).filter(Pool.id == pool_id).first()
        if not pool:
            return None

        results = (
            self.db.query(
                VisitorRecord.weekday,
                extract('hour', VisitorRecord.timestamp).label('hour'),
                func.avg(VisitorRecord.visitor_count).label('avg_visitors')
            )
            .filter(
                VisitorRecord.pool_id == pool_id,
                extract('hour', VisitorRecord.timestamp) >= self.POOL_OPEN_HOUR,
                extract('hour', VisitorRecord.timestamp) <= self.POOL_CLOSE_HOUR
            )
            .group_by(VisitorRecord.weekday, extract('hour', VisitorRecord.timestamp))
            .all()
        )

        if not results:
            return HeatmapData(
                pool_id=pool_id,
                pool_name=pool.name,
                data=[],
                min_value=0,
                max_value=0
            )

        cells = []
        values = []
        for row in results:
            value = round(float(row.avg_visitors), 1)
            cells.append(HeatmapCell(
                weekday=row.weekday,
                hour=int(row.hour),
                value=value
            ))
            values.append(value)

        return HeatmapData(
            pool_id=pool_id,
            pool_name=pool.name,
            data=cells,
            min_value=min(values) if values else 0,
            max_value=max(values) if values else 0
        )

    def get_daily_summary(
        self,
        pool_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[DailySummary]:
        """Get daily summary statistics."""
        query = self.db.query(
            func.date(VisitorRecord.timestamp).label('date'),
            func.min(VisitorRecord.visitor_count).label('min_visitors'),
            func.max(VisitorRecord.visitor_count).label('max_visitors'),
            func.avg(VisitorRecord.visitor_count).label('avg_visitors'),
            func.count(VisitorRecord.id).label('total_readings')
        ).filter(VisitorRecord.pool_id == pool_id)

        if start_date:
            start_dt = datetime.combine(start_date, datetime.min.time())
            query = query.filter(VisitorRecord.timestamp >= start_dt)

        if end_date:
            end_dt = datetime.combine(end_date, datetime.max.time())
            query = query.filter(VisitorRecord.timestamp <= end_dt)

        results = (
            query
            .group_by(func.date(VisitorRecord.timestamp))
            .order_by(func.date(VisitorRecord.timestamp).desc())
            .all()
        )

        return [
            DailySummary(
                date=row.date,
                pool_id=pool_id,
                min_visitors=row.min_visitors,
                max_visitors=row.max_visitors,
                avg_visitors=round(float(row.avg_visitors), 1),
                total_readings=row.total_readings
            )
            for row in results
        ]

    def get_trends(
        self,
        pool_id: int,
        period: str = "weekly"
    ) -> Optional[TrendData]:
        """Get trend analysis by week or month."""
        pool = self.db.query(Pool).filter(Pool.id == pool_id).first()
        if not pool:
            return None

        if period == "weekly":
            # Group by year-week
            period_expr = func.concat(
                extract('year', VisitorRecord.timestamp),
                '-W',
                func.lpad(func.cast(extract('week', VisitorRecord.timestamp), String), 2, '0')
            )
        else:
            # Group by year-month
            period_expr = func.concat(
                extract('year', VisitorRecord.timestamp),
                '-',
                func.lpad(func.cast(extract('month', VisitorRecord.timestamp), String), 2, '0')
            )

        results = (
            self.db.query(
                period_expr.label('period'),
                func.avg(VisitorRecord.visitor_count).label('avg_visitors'),
                func.max(VisitorRecord.visitor_count).label('peak_visitors'),
                func.count(VisitorRecord.id).label('total_readings')
            )
            .filter(VisitorRecord.pool_id == pool_id)
            .group_by(period_expr)
            .order_by(period_expr.desc())
            .limit(52 if period == "weekly" else 12)
            .all()
        )

        data_points = [
            TrendDataPoint(
                period=row.period,
                average_visitors=round(float(row.avg_visitors), 1),
                peak_visitors=row.peak_visitors,
                total_readings=row.total_readings
            )
            for row in results
        ]

        # Reverse to show oldest first
        data_points.reverse()

        return TrendData(
            pool_id=pool_id,
            pool_name=pool.name,
            period_type=period,
            data=data_points
        )

    def get_peak_hours(self, pool_id: int, weekday: Optional[str] = None) -> dict:
        """Get peak hours analysis (during pool hours only)."""
        query = (
            self.db.query(
                extract('hour', VisitorRecord.timestamp).label('hour'),
                func.avg(VisitorRecord.visitor_count).label('avg_visitors'),
                func.max(VisitorRecord.visitor_count).label('max_visitors')
            )
            .filter(
                VisitorRecord.pool_id == pool_id,
                extract('hour', VisitorRecord.timestamp) >= self.POOL_OPEN_HOUR,
                extract('hour', VisitorRecord.timestamp) <= self.POOL_CLOSE_HOUR
            )
        )

        if weekday:
            query = query.filter(VisitorRecord.weekday == weekday)

        results = (
            query
            .group_by(extract('hour', VisitorRecord.timestamp))
            .order_by(func.avg(VisitorRecord.visitor_count).desc())
            .all()
        )

        if not results:
            return {"peak_hour": None, "quietest_hour": None, "by_hour": []}

        by_hour = [
            {
                "hour": int(row.hour),
                "average": round(float(row.avg_visitors), 1),
                "max": row.max_visitors
            }
            for row in results
        ]

        return {
            "peak_hour": int(results[0].hour) if results else None,
            "quietest_hour": int(results[-1].hour) if results else None,
            "by_hour": sorted(by_hour, key=lambda x: x["hour"])
        }

    def get_weekday_average_up_to_now(self, pool_id: int) -> Optional[WeekdayAverageUpToNow]:
        """Get average visitor count for current weekday up to current time of day."""
        pool = self.db.query(Pool).filter(Pool.id == pool_id).first()
        if not pool:
            return None

        # Get current time in pool's timezone
        tz = pytz.timezone(pool.timezone)
        now = datetime.now(tz)
        current_weekday = now.strftime("%A")
        current_hour = now.hour
        current_minute = now.minute

        # Query historical data for same weekday, only hours from pool open to current hour
        results = (
            self.db.query(
                func.avg(VisitorRecord.visitor_count).label('avg_visitors'),
                func.min(VisitorRecord.visitor_count).label('min_visitors'),
                func.max(VisitorRecord.visitor_count).label('max_visitors'),
                func.count(VisitorRecord.id).label('sample_count')
            )
            .filter(
                VisitorRecord.pool_id == pool_id,
                VisitorRecord.weekday == current_weekday,
                extract('hour', VisitorRecord.timestamp) >= self.POOL_OPEN_HOUR,
                extract('hour', VisitorRecord.timestamp) <= current_hour
            )
            .first()
        )

        if not results or results.sample_count == 0:
            return WeekdayAverageUpToNow(
                pool_id=pool_id,
                pool_name=pool.name,
                weekday=current_weekday,
                current_time=now.strftime("%H:%M"),
                average_visitors=0,
                min_visitors=0,
                max_visitors=0,
                sample_count=0
            )

        return WeekdayAverageUpToNow(
            pool_id=pool_id,
            pool_name=pool.name,
            weekday=current_weekday,
            current_time=now.strftime("%H:%M"),
            average_visitors=round(float(results.avg_visitors), 1),
            min_visitors=results.min_visitors,
            max_visitors=results.max_visitors,
            sample_count=results.sample_count
        )
