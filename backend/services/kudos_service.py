import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.kudos import Kudos
from backend.services import activity_service

logger = logging.getLogger("runbanditsrun.services.kudos")


def give_kudos(db: Session, activity_id: int, user_id: int) -> dict:
    logger.info(f"User {user_id} attempting to give kudos to activity {activity_id}")
    activity = activity_service.get_activity(db, activity_id, user_id)
    if not activity:
        logger.warning(f"Activity {activity_id} not found or not visible to user {user_id}")
        raise LookupError("Activity not found or not visible")
    existing = (
        db.query(Kudos).filter(Kudos.activity_id == activity_id, Kudos.user_id == user_id).first()
    )
    if existing:
        logger.warning(f"User {user_id} already gave kudos to activity {activity_id}")
        raise ValueError("Already gave kudos")
    db.add(Kudos(activity_id=activity_id, user_id=user_id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning(f"Integrity error giving kudos to activity {activity_id} by user {user_id}")
        raise LookupError("Activity not found or not visible")
    db.refresh(activity)
    logger.info(f"User {user_id} gave kudos to activity {activity_id}")
    return {"kudos_count": len(activity.kudos), "user_has_kudos": True}


def remove_kudos(db: Session, activity_id: int, user_id: int) -> dict:
    logger.info(f"User {user_id} attempting to remove kudos from activity {activity_id}")
    kudos = (
        db.query(Kudos).filter(Kudos.activity_id == activity_id, Kudos.user_id == user_id).first()
    )
    if not kudos:
        logger.warning(f"Kudos not found for activity {activity_id} by user {user_id}")
        raise LookupError("Kudos not found")
    db.delete(kudos)
    db.commit()
    activity = activity_service.get_activity(db, activity_id, user_id)
    if activity:
        db.refresh(activity)
        logger.info(f"User {user_id} removed kudos from activity {activity_id}")
        return {"kudos_count": len(activity.kudos), "user_has_kudos": False}
    logger.warning(f"Activity {activity_id} not found after removing kudos")
    return {"kudos_count": 0, "user_has_kudos": False}
