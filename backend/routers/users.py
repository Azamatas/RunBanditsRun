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


@router.get("/me/friends", response_model=list[UserOut])
def list_friends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.debug(f"User {current_user.id} requested friends list")
    return user_service.get_friends(db, current_user.id)


@router.get("/me/friends/incoming", response_model=list[UserOut])
def list_friends_from(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.debug(f"User {current_user.id} requested incoming friends list")
    return user_service.get_friends_from(db, current_user.id)


@router.get("/me/friend-requests/pending", response_model=list[UserOut])
def list_pending_friend_requests(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.debug(f"User {current_user.id} requested pending friend requests")
    return user_service.get_pending_friend_requests(db, current_user.id)


@router.get("/me/friend-requests/incoming")
def list_incoming_friend_requests(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.debug(f"User {current_user.id} requested incoming friend requests")
    return user_service.get_incoming_friend_requests(db, current_user.id)


@router.get("/me/friend-requests/sent")
def list_sent_friend_requests(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.debug(f"User {current_user.id} requested sent friend requests")
    return user_service.get_sent_friend_requests(db, current_user.id)


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


@router.post("/{user_id}/friend-request", status_code=201)
def send_friend_request(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} sending friend request to user {user_id}")
    try:
        status = user_service.send_friend_request(db, current_user.id, user_id)
        logger.info(f"Friend request status: {status}")
    except ValueError as e:
        logger.warning(f"Friend request failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": status}


@router.post("/{user_id}/accept-friend", status_code=200)
def accept_friend_request(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} accepting friend request from user {user_id}")
    try:
        status = user_service.accept_friend_request(db, current_user.id, user_id)
        logger.info(f"Accept friend request status: {status}")
    except LookupError as e:
        logger.warning(f"Accept friend request failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    return {"status": status}


@router.delete("/{user_id}/friend", status_code=204)
def remove_friend(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    logger.info(f"User {current_user.id} removing friend {user_id}")
    try:
        user_service.remove_friend(db, current_user.id, user_id)
        logger.info(f"User {current_user.id} removed friend {user_id}")
    except LookupError as e:
        logger.warning(f"Remove friend failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
