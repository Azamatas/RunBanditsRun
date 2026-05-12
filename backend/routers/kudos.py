from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.kudos import Kudos
from backend.services import activity_service
from backend.routers.deps import get_current_user

router = APIRouter(prefix="/activities", tags=["kudos"])


@router.post("/{activity_id}/kudos", status_code=201)
def give_kudos(activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    activity = activity_service.get_activity(db, activity_id, current_user.id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found or not visible")
    existing = db.query(Kudos).filter(Kudos.activity_id == activity_id, Kudos.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already gave kudos")
    db.add(Kudos(activity_id=activity_id, user_id=current_user.id))
    db.commit()
    db.refresh(activity)
    return {"kudos_count": len(activity.kudos)}


@router.delete("/{activity_id}/kudos", status_code=204)
def remove_kudos(activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kudos = db.query(Kudos).filter(Kudos.activity_id == activity_id, Kudos.user_id == current_user.id).first()
    if not kudos:
        raise HTTPException(status_code=404, detail="Kudos not found")
    db.delete(kudos)
    db.commit()
