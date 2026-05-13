from sqlalchemy.orm import Session
from backend.models.kudos import Kudos
from backend.models.activity import Activity


def give_kudos(db: Session, activity_id: int, user_id: int) -> dict:
    existing = db.query(Kudos).filter(
        Kudos.activity_id == activity_id,
        Kudos.user_id == user_id
    ).first()
    if existing:
        raise ValueError("Already gave kudos")
    db.add(Kudos(activity_id=activity_id, user_id=user_id))
    db.commit()
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
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
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    return {"kudos_count": len(activity.kudos) if activity else 0, "user_has_kudos": False}