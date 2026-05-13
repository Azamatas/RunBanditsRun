from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.models.kudos import Kudos
from backend.services import activity_service


def give_kudos(db: Session, activity_id: int, user_id: int) -> dict:
    activity = activity_service.get_activity(db, activity_id, user_id)
    if not activity:
        raise LookupError("Activity not found or not visible")
    existing = db.query(Kudos).filter(
        Kudos.activity_id == activity_id,
        Kudos.user_id == user_id
    ).first()
    if existing:
        raise ValueError("Already gave kudos")
    db.add(Kudos(activity_id=activity_id, user_id=user_id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise LookupError("Activity not found or not visible")
    db.refresh(activity)
    return {"kudos_count": len(activity.kudos), "user_has_kudos": True}


def remove_kudos(db: Session, activity_id: int, user_id: int) -> dict:
    kudos = db.query(Kudos).filter(
        Kudos.activity_id == activity_id,
        Kudos.user_id == user_id
    ).first()
    if not kudos:
        raise LookupError("Kudos not found")
    db.delete(kudos)
    db.commit()
    activity = activity_service.get_activity(db, activity_id, user_id)
    if activity:
        db.refresh(activity)
        return {"kudos_count": len(activity.kudos), "user_has_kudos": False}
    return {"kudos_count": 0, "user_has_kudos": False}