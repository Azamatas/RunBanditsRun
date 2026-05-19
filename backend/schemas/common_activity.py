from pydantic import BaseModel, field_validator

from backend.models.activity import SportType


class CommonActivityCreate(BaseModel):
    name: str
    sport_type: SportType
    polyline: str

    @field_validator("polyline")
    @classmethod
    def polyline_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("polyline must not be empty")
        return v


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
