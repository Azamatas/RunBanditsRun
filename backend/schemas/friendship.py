from datetime import datetime

from pydantic import BaseModel

from backend.schemas.user import UserOut


class FriendRequestOut(BaseModel):
    id: int
    requester_id: int
    requester: UserOut
    status: str
    created_at: datetime | None

    model_config = {"from_attributes": True}


class SentFriendRequestOut(BaseModel):
    id: int
    addressee_id: int
    addressee: UserOut
    status: str
    created_at: datetime | None

    model_config = {"from_attributes": True}
