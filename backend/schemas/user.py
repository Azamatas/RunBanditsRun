from datetime import datetime
from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    username: str
    bio: str | None
    location: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    username: str | None = None
    bio: str | None = None
    location: str | None = None
