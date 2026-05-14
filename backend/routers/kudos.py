import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.routers.deps import get_current_user
from backend.services import kudos_service

logger = logging.getLogger("runbanditsrun.routers.kudos")

router = APIRouter(prefix="/activities", tags=["kudos"])


@router.post("/{activity_id}/kudos", status_code=201)
def give_kudos(
    activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} giving kudos to activity {activity_id}")
    try:
        result = kudos_service.give_kudos(db, activity_id, current_user.id)
        logger.info(f"User {current_user.id} gave kudos to activity {activity_id}")
        return result
    except LookupError as e:
        logger.warning(f"Kudos failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.warning(f"Kudos failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{activity_id}/kudos", status_code=204)
def remove_kudos(
    activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} removing kudos from activity {activity_id}")
    try:
        kudos_service.remove_kudos(db, activity_id, current_user.id)
        logger.info(f"User {current_user.id} removed kudos from activity {activity_id}")
    except LookupError:
        logger.warning(f"Kudos not found for activity {activity_id} by user {current_user.id}")
        raise HTTPException(status_code=404, detail="Kudos not found")
