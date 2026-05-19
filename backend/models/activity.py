import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.geometry import PATH_SRID

if TYPE_CHECKING:
    from backend.models.common_activity import CommonActivity
    from backend.models.kudos import Kudos
    from backend.models.user import User


class SportType(enum.StrEnum):
    RUN = "run"
    RIDE = "ride"
    WALK = "walk"
    HIKE = "hike"


class Visibility(enum.StrEnum):
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"


activity_athletes = Table(
    "activity_athletes",
    Base.metadata,
    Column("activity_id", ForeignKey("activities.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    sport_type: Mapped[SportType] = mapped_column(
        Enum(SportType, name="sport_type", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    distance: Mapped[float | None] = mapped_column(Float)
    duration: Mapped[int | None] = mapped_column(Integer)
    elevation: Mapped[float | None] = mapped_column(Float)
    polyline: Mapped[str | None] = mapped_column(Text)
    path: Mapped[Any] = mapped_column(Geometry(geometry_type="LINESTRING", srid=PATH_SRID))
    visibility: Mapped[Visibility] = mapped_column(
        Enum(Visibility, name="visibility", values_callable=lambda obj: [e.value for e in obj]),
        default=Visibility.PUBLIC,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    common_activity_id: Mapped[int | None] = mapped_column(ForeignKey("common_activities.id"))

    owner: Mapped["User"] = relationship(
        "User", foreign_keys=[owner_id], back_populates="activities"
    )
    tagged_athletes: Mapped[list["User"]] = relationship("User", secondary=activity_athletes)
    kudos: Mapped[list["Kudos"]] = relationship("Kudos", back_populates="activity")
    common_activity: Mapped["CommonActivity"] = relationship("CommonActivity", back_populates="activities")
