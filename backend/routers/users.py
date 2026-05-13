from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.activity import SportType
from backend.schemas.user import UserOut, UserUpdate
from backend.schemas.activity import ActivityOut
from backend.services import user_service
from backend.routers.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(body: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return user_service.update_user(db, current_user, body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/followers", response_model=list[UserOut])
def list_followers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.get_followers(db, current_user.id)


@router.get("/me/following", response_model=list[UserOut])
def list_following(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.get_following(db, current_user.id)


@router.get("/me/pending", response_model=list[UserOut])
def list_pending_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.get_pending_requests(db, current_user.id)


@router.get("/me/requests")
def list_pending_requests_detailed(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.get_pending_requests_detailed(db, current_user.id)


@router.get("/me/sent-requests")
def list_sent_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.get_sent_requests(db, current_user.id)


@router.get("/search")
def search_users(q: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.search_users(db, current_user.id, q)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/activities", response_model=list[ActivityOut])
def list_user_activities(
    user_id: int,
    sport_type: Optional[SportType] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = user_service.get_user_activities(db, user_id, current_user.id, sport_type=sport_type, offset=offset, limit=limit)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.post("/{user_id}/follow", status_code=201)
def follow_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        status = user_service.follow_user(db, current_user.id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": status}


@router.post("/{user_id}/accept", status_code=200)
def accept_follow(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        status = user_service.accept_follow(db, current_user.id, user_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": status}


@router.delete("/{user_id}/unfollow", status_code=204)
def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        user_service.unfollow_user(db, current_user.id, user_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))