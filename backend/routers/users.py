import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.activity import SportType
from backend.models.user import User
from backend.routers.deps import get_current_user
from backend.schemas.activity import ActivityOut
from backend.schemas.user import UserOut, UserUpdate
from backend.services import user_service

logger = logging.getLogger("runbanditsrun.routers.users")

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    logger.debug(f"User {current_user.id} requested their profile")
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    body: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} updating profile")
    try:
        result = user_service.update_user(db, current_user, body.model_dump(exclude_none=True))
        logger.info(f"User {current_user.id} profile updated")
        return result
    except ValueError as e:
        logger.warning(f"User {current_user.id} profile update failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/followers", response_model=list[UserOut])
def list_followers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.debug(f"User {current_user.id} requested followers list")
    return user_service.get_followers(db, current_user.id)


@router.get("/me/following", response_model=list[UserOut])
def list_following(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.debug(f"User {current_user.id} requested following list")
    return user_service.get_following(db, current_user.id)


@router.get("/me/pending", response_model=list[UserOut])
def list_pending_requests(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.debug(f"User {current_user.id} requested pending follow requests")
    return user_service.get_pending_requests(db, current_user.id)


@router.get("/me/requests")
def list_pending_requests_detailed(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.debug(f"User {current_user.id} requested detailed pending requests")
    return user_service.get_pending_requests_detailed(db, current_user.id)


@router.get("/me/sent-requests")
def list_sent_requests(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.debug(f"User {current_user.id} requested sent follow requests")
    return user_service.get_sent_requests(db, current_user.id)


@router.get("/search")
def search_users(
    q: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.debug(f"User {current_user.id} searching users with query: {q}")
    return user_service.search_users(db, current_user.id, q)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    logger.debug(f"Requested user profile: {user_id}")
    user = user_service.get_user(db, user_id)
    if not user:
        logger.warning(f"User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/activities", response_model=list[ActivityOut])
def list_user_activities(
    user_id: int,
    sport_type: SportType | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(f"User {current_user.id} requested activities for user {user_id}")
    result = user_service.get_user_activities(
        db, user_id, current_user.id, sport_type=sport_type, offset=offset, limit=limit
    )
    if result is None:
        logger.warning(f"User {user_id} not found when fetching activities")
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.post("/{user_id}/follow", status_code=201)
def follow_user(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} following user {user_id}")
    try:
        status = user_service.follow_user(db, current_user.id, user_id)
        logger.info(f"Follow status: {status}")
    except ValueError as e:
        logger.warning(f"Follow failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": status}


@router.post("/{user_id}/accept", status_code=200)
def accept_follow(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} accepting follow from user {user_id}")
    try:
        status = user_service.accept_follow(db, current_user.id, user_id)
        logger.info(f"Accept follow status: {status}")
    except LookupError as e:
        logger.warning(f"Accept follow failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": status}


@router.delete("/{user_id}/unfollow", status_code=204)
def unfollow_user(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} unfollowing user {user_id}")
    try:
        user_service.unfollow_user(db, current_user.id, user_id)
        logger.info(f"User {current_user.id} unfollowed user {user_id}")
    except LookupError as e:
        logger.warning(f"Unfollow failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
