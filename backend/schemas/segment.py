from datetime import datetime
from pydantic import BaseModel


class SegmentCreate(BaseModel):
    name: str
    polyline: str | None = None
    distance: float | None = None


class SegmentOut(BaseModel):
    id: int
    name: str
    polyline: str | None
    distance: float | None

    model_config = {"from_attributes": True}


class SegmentEffortOut(BaseModel):
    id: int
    segment_id: int
    activity_id: int
    athlete_id: int
    elapsed_time: int
    started_at: datetime | None

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    athlete_id: int
    athlete_name: str
    best_time: int
    rank: int