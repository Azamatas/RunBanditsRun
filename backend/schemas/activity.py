from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from backend.models.activity import SportType, Visibility

Int32 = Annotated[int, Field(ge=0, le=2147483647)]


class ActivityCreate(BaseModel):
    title: str
    sport_type: SportType
    distance: float | None = None
    duration: Int32 | None = None
    elevation: float | None = None
    polyline: str | None = None
    visibility: Visibility = Visibility.PUBLIC
    started_at: datetime | None = None
    tagged_athlete_ids: list[Annotated[int, Field(ge=1)]] = []


class ActivityOut(BaseModel):
    id: int
    owner_id: int
    owner_username: str | None = None
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
    user_has_kudos: bool = False

    model_config = {"from_attributes": True}


class ActivityUpdate(BaseModel):
    title: str | None = None
    sport_type: SportType | None = None
    distance: float | None = None
    duration: Int32 | None = None
    elevation: float | None = None
    polyline: str | None = None
    visibility: Visibility | None = None
    started_at: datetime | None = None
