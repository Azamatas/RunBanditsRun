from typing import TYPE_CHECKING, Any

from geoalchemy2 import Geometry
from sqlalchemy import Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.activity import SportType

if TYPE_CHECKING:
    from backend.models.activity import Activity


class CommonActivity(Base):
    __tablename__ = "common_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    polyline: Mapped[str | None] = mapped_column(Text)
    path: Mapped[Any] = mapped_column(Geometry(geometry_type="LINESTRING", srid=4326))
    distance: Mapped[float | None] = mapped_column(Float)
    sport_type: Mapped[SportType | None] = mapped_column(
        Enum(SportType, name="sport_type", values_callable=lambda obj: [e.value for e in obj])
    )

    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="common_activity")
