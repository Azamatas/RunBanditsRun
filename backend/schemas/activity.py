from datetime import datetime
from pydantic import BaseModel
from backend.models.activity import SportType, Visibility


class ActivityCreate(BaseModel):
    title: str
    sport_type: SportType
    distance: float | None = None
    duration: int | None = None
    elevation: float | None = None
    polyline: str | None = None
    visibility: Visibility = Visibility.PUBLIC
    started_at: datetime | None = None
    tagged_athlete_ids: list[int] = []


class ActivityOut(BaseModel):
    id: int
    owner_id: int
    title: str
    sport_type: SportType
    distance: float | None
    duration: int | None
    elevation: float | None
    polyline: str | None
    visibility: Visibility
    started_at: datetime | None
    created_at: datetime
    kudos_count: int = 0

    model_config = {"from_attributes": True}


class ActivityUpdate(BaseModel):
    title: str | None = None
    sport_type: SportType | None = None
    distance: float | None = None
    duration: int | None = None
    elevation: float | None = None
    polyline: str | None = None
    visibility: Visibility | None = None
    started_at: datetime | None = None
