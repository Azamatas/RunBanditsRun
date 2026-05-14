from pydantic import BaseModel

from backend.models.activity import SportType


class CommonActivityOut(BaseModel):
    id: int
    name: str
    polyline: str | None
    distance: float | None
    sport_type: SportType | None

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    athlete_id: int
    athlete_name: str
    best_time: int
    rank: int
