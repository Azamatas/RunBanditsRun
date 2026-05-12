from datetime import datetime
from pydantic import BaseModel


class StatsTotals(BaseModel):
    count: int
    total_distance: float
    total_elevation: float
    total_duration: int


class PersonalRecord(BaseModel):
    segment_id: int
    best_time: int


class StatsResponse(BaseModel):
    totals: dict[str, StatsTotals]
    personal_records: list[PersonalRecord]