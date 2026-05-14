import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.common_activity import CommonActivity
from backend.models.user import User

logger = logging.getLogger("runbanditsrun.services.common_activity")


def get_common_activity(db: Session, common_activity_id: int) -> CommonActivity | None:
    logger.debug(f"Fetching common activity by ID: {common_activity_id}")
    return db.query(CommonActivity).filter(CommonActivity.id == common_activity_id).first()


def list_common_activities(
    db: Session,
    sport_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[CommonActivity]:
    logger.debug(f"Listing common activities with offset={offset}, limit={limit}")
    query = db.query(CommonActivity)
    if sport_type:
        query = query.filter(CommonActivity.sport_type == sport_type)
    query = query.offset(offset).limit(limit)
    return query.all()


def get_leaderboard(db: Session, common_activity_id: int, limit: int = 10) -> list[dict]:
    logger.debug(f"Generating leaderboard for common activity {common_activity_id} with limit={limit}")
    from backend.models.activity import Activity

    results = (
        db.query(
            User.id.label("athlete_id"),
            User.username.label("athlete_name"),
            func.min(Activity.duration).label("best_time"),
        )
        .join(User, User.id == Activity.owner_id)
        .join(CommonActivity, CommonActivity.id == Activity.common_activity_id)
        .filter(CommonActivity.id == common_activity_id, Activity.duration.isnot(None))
        .group_by(User.id, User.username)
        .order_by(func.min(Activity.duration))
        .limit(limit)
        .all()
    )

    return [
        {
            "athlete_id": r.athlete_id,
            "athlete_name": r.athlete_name,
            "best_time": r.best_time,
            "rank": idx + 1,
        }
        for idx, r in enumerate(results)
    ]
