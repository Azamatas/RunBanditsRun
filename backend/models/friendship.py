import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base

if TYPE_CHECKING:
    from backend.models.user import User


class FriendshipStatus(enum.StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"


class Friendship(Base):
    __tablename__ = "friendships"

    id: Mapped[int] = mapped_column(primary_key=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    addressee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[FriendshipStatus] = mapped_column(
        Enum(
            FriendshipStatus,
            name="friendship_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=FriendshipStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    requester: Mapped["User"] = relationship(
        "User", foreign_keys=[requester_id], back_populates="sent_requests"
    )
    addressee: Mapped["User"] = relationship(
        "User", foreign_keys=[addressee_id], back_populates="received_requests"
    )
