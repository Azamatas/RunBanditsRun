from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

if TYPE_CHECKING:
    from backend.models.user import User
    from backend.models.activity import Activity


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    polyline: Mapped[str | None] = mapped_column(Text)
    distance: Mapped[float | None] = mapped_column(Float)

    efforts: Mapped[list["SegmentEffort"]] = relationship("SegmentEffort", back_populates="segment")


class SegmentEffort(Base):
    __tablename__ = "segment_efforts"

    id: Mapped[int] = mapped_column(primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), nullable=False)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), nullable=False)
    athlete_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    elapsed_time: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)

    segment: Mapped["Segment"] = relationship("Segment", back_populates="efforts")
    activity: Mapped["Activity"] = relationship("Activity", back_populates="segment_efforts")
    athlete: Mapped["User"] = relationship("User")
