import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.activity import Activity, SportType

logger = logging.getLogger("runbanditsrun.services.stats")


def get_totals(db: Session, user_id: int, sport_type: SportType | None = None) -> dict:
    logger.debug(f"Calculating totals for user {user_id} with sport_type={sport_type}")
    query = db.query(
        Activity.sport_type,
        func.count(Activity.id).label("count"),
        func.sum(Activity.distance).label("total_distance"),
        func.sum(Activity.elevation).label("total_elevation"),
        func.sum(Activity.duration).label("total_duration"),
    ).filter(Activity.owner_id == user_id)
    if sport_type:
        query = query.filter(Activity.sport_type == sport_type)
    rows = query.group_by(Activity.sport_type).all()

    return {
        row.sport_type: {
            "count": row.count,
            "total_distance": row.total_distance or 0,
            "total_elevation": row.total_elevation or 0,
            "total_duration": row.total_duration or 0,
        }
        for row in rows
    }


def get_personal_records(db: Session, user_id: int) -> list[dict]:
    logger.debug(f"Fetching personal records for user {user_id}")
    # TODO
    return []
