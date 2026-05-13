from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.activity import SportType
from backend.schemas.activity import ActivityCreate, ActivityOut, ActivityUpdate
from backend.services import activity_service
from backend.routers.deps import get_current_user

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/", response_model=list[ActivityOut])
def list_activities(
    sport_type: Optional[SportType] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return activity_service.list_activities(db, current_user.id, sport_type=sport_type, offset=offset, limit=limit)


@router.post("/", response_model=ActivityOut)
def create_activity(body: ActivityCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = body.model_dump(exclude={"tagged_athlete_ids"})
    activity = activity_service.create_activity(db, current_user.id, data, body.tagged_athlete_ids)
    return activity_service.enrich_activity(activity, current_user.id)


@router.get("/{activity_id}", response_model=ActivityOut)
def get_activity(activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    activity = activity_service.get_activity(db, activity_id, current_user.id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found or not visible")
    return activity_service.enrich_activity(activity, current_user.id)


@router.patch("/{activity_id}", response_model=ActivityOut)
def update_activity(activity_id: int, body: ActivityUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    activity = activity_service.update_activity(db, activity_id, current_user.id, body.model_dump(exclude_none=True))
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity_service.enrich_activity(activity, current_user.id)


@router.delete("/{activity_id}", status_code=204)
def delete_activity(activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not activity_service.delete_activity(db, activity_id, current_user.id):
        raise HTTPException(status_code=404, detail="Activity not found")