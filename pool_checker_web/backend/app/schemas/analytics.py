from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class WeekdayAverage(BaseModel):
    weekday: str
    hour: int
    average_visitors: float
    sample_count: int


class HeatmapCell(BaseModel):
    weekday: str
    hour: int
    value: float


class HeatmapData(BaseModel):
    pool_id: int
    pool_name: str
    data: List[HeatmapCell]
    min_value: float
    max_value: float


class DailySummary(BaseModel):
    date: date
    pool_id: int
    min_visitors: int
    max_visitors: int
    avg_visitors: float
    total_readings: int


class TrendDataPoint(BaseModel):
    period: str  # e.g., "2024-W01" for week, "2024-01" for month
    average_visitors: float
    peak_visitors: int
    total_readings: int


class TrendData(BaseModel):
    pool_id: int
    pool_name: str
    period_type: str  # "weekly" or "monthly"
    data: List[TrendDataPoint]


class WeekdayAverageUpToNow(BaseModel):
    pool_id: int
    pool_name: str
    weekday: str
    current_time: str
    average_visitors: float
    min_visitors: int
    max_visitors: int
    sample_count: int
