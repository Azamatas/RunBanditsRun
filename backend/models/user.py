from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base

if TYPE_CHECKING:
    from backend.models.activity import Activity
    from backend.models.friendship import Friendship
    from backend.models.kudos import Kudos


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="owner", foreign_keys="Activity.owner_id"
    )
    sent_requests: Mapped[list["Friendship"]] = relationship(
        "Friendship", foreign_keys="Friendship.requester_id", back_populates="requester"
    )
    received_requests: Mapped[list["Friendship"]] = relationship(
        "Friendship", foreign_keys="Friendship.addressee_id", back_populates="addressee"
    )
    kudos_given: Mapped[list["Kudos"]] = relationship("Kudos", back_populates="user")
