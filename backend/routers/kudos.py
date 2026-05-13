from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.services import kudos_service
from backend.routers.deps import get_current_user

router = APIRouter(prefix="/activities", tags=["kudos"])


@router.post("/{activity_id}/kudos", status_code=201)
def give_kudos(activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return kudos_service.give_kudos(db, activity_id, current_user.id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{activity_id}/kudos", status_code=204)
def remove_kudos(activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        kudos_service.remove_kudos(db, activity_id, current_user.id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Kudos not found")