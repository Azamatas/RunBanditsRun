import logging

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.models.activity import Activity, Visibility
from backend.models.friendship import Friendship, FriendshipStatus
from backend.models.user import User
from backend.services import auth_service

logger = logging.getLogger("runbanditsrun.services.user")


def get_user(db: Session, user_id: int) -> User | None:
    logger.debug(f"Fetching user by ID: {user_id}")
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, current_user: User, updates: dict) -> User:
    logger.info(f"Updating user {current_user.id} with changes: {list(updates.keys())}")
    if "username" in updates and updates["username"] != current_user.username:
        existing = auth_service.get_user_by_username(db, updates["username"])
        if existing:
            logger.warning(f"Username {updates['username']} already taken by user {existing.id}")
            raise ValueError("Username already taken")
    for field, value in updates.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    logger.info(f"User {current_user.id} updated successfully")
    return current_user


def get_followers(db: Session, user_id: int) -> list[User]:
    logger.debug(f"Fetching followers for user {user_id}")
    requester_ids = select(Friendship.requester_id).where(
        Friendship.addressee_id == user_id, Friendship.status == FriendshipStatus.ACCEPTED
    )
    return db.query(User).filter(User.id.in_(requester_ids)).all()


def get_following(db: Session, user_id: int) -> list[User]:
    logger.debug(f"Fetching following list for user {user_id}")
    addressee_ids = select(Friendship.addressee_id).where(
        Friendship.requester_id == user_id, Friendship.status == FriendshipStatus.ACCEPTED
    )
    return db.query(User).filter(User.id.in_(addressee_ids)).all()


def get_pending_requests(db: Session, user_id: int) -> list[User]:
    logger.debug(f"Fetching pending follow requests for user {user_id}")
    requester_ids = select(Friendship.requester_id).where(
        Friendship.addressee_id == user_id, Friendship.status == FriendshipStatus.PENDING
    )
    return db.query(User).filter(User.id.in_(requester_ids)).all()


def get_pending_requests_detailed(db: Session, user_id: int) -> list[dict]:
    from backend.schemas.user import UserOut

    logger.debug(f"Fetching detailed pending requests for user {user_id}")
    friendships = (
        db.query(Friendship)
        .filter(Friendship.addressee_id == user_id, Friendship.status == FriendshipStatus.PENDING)
        .all()
    )
    return [
        {
            "id": f.id,
            "requester_id": f.requester_id,
            "requester": UserOut.model_validate(
                db.query(User).filter(User.id == f.requester_id).first()
            ),
            "status": f.status.value,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in friendships
    ]


def get_sent_requests(db: Session, user_id: int) -> list[dict]:
    logger.debug(f"Fetching sent follow requests for user {user_id}")
    friendships = (
        db.query(Friendship)
        .filter(Friendship.requester_id == user_id, Friendship.status == FriendshipStatus.PENDING)
        .all()
    )
    return [
        {"id": f.id, "addressee_id": f.addressee_id, "status": f.status.value} for f in friendships
    ]


def search_users(db: Session, current_user_id: int, query: str = "", limit: int = 50) -> list[User]:
    logger.debug(f"User {current_user_id} searching users with query: {query}")
    q = db.query(User).filter(User.id != current_user_id)
    if query:
        q = q.filter(User.username.ilike(f"%{query}%"))
    return q.limit(limit).all()


def follow_user(db: Session, current_user_id: int, target_user_id: int) -> str:
    logger.info(f"User {current_user_id} attempting to follow user {target_user_id}")
    if current_user_id == target_user_id:
        logger.warning(f"User {current_user_id} attempted to follow themselves")
        raise ValueError("Cannot follow yourself")
    existing = (
        db.query(Friendship)
        .filter(
            Friendship.requester_id == current_user_id, Friendship.addressee_id == target_user_id
        )
        .first()
    )
    if existing:
        logger.warning(
            f"User {current_user_id} already has a request pending for user {target_user_id}"
        )
        raise ValueError("Request already sent")
    db.add(Friendship(requester_id=current_user_id, addressee_id=target_user_id))
    db.commit()
    logger.info(f"User {current_user_id} sent follow request to user {target_user_id}")
    return "pending"


def accept_follow(db: Session, current_user_id: int, requester_id: int) -> str:
    logger.info(f"User {current_user_id} accepting follow request from user {requester_id}")
    friendship = (
        db.query(Friendship)
        .filter(
            Friendship.requester_id == requester_id,
            Friendship.addressee_id == current_user_id,
            Friendship.status == FriendshipStatus.PENDING,
        )
        .first()
    )
    if not friendship:
        logger.warning(
            f"No pending follow request found from user {requester_id} to user {current_user_id}"
        )
        raise LookupError("No pending request")
    friendship.status = FriendshipStatus.ACCEPTED
    db.commit()
    logger.info(f"User {current_user_id} accepted follow request from user {requester_id}")
    return "accepted"


def unfollow_user(db: Session, current_user_id: int, target_user_id: int) -> None:
    logger.info(f"User {current_user_id} unfollowing user {target_user_id}")
    friendship = (
        db.query(Friendship)
        .filter(
            (
                (Friendship.requester_id == current_user_id)
                & (Friendship.addressee_id == target_user_id)
            )
            | (
                (Friendship.addressee_id == current_user_id)
                & (Friendship.requester_id == target_user_id)
            )
        )
        .first()
    )
    if not friendship:
        logger.warning(
            f"No friendship found between user {current_user_id} and user {target_user_id}"
        )
        raise LookupError("No friendship found")
    db.delete(friendship)
    db.commit()
    logger.info(f"User {current_user_id} unfollowed user {target_user_id}")


def get_user_activities(
    db: Session, user_id: int, viewer_id: int, sport_type=None, offset: int = 0, limit: int = 20
) -> list[dict] | None:
    from backend.services.activity_service import enrich_activity

    logger.debug(f"Fetching activities for user {user_id} viewed by user {viewer_id}")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        logger.warning(f"User {user_id} not found")
        return None
    if user_id == viewer_id:
        visibility_filter = Activity.owner_id == viewer_id
    else:
        is_friend = (
            db.query(Friendship)
            .filter(
                Friendship.status == FriendshipStatus.ACCEPTED,
                ((Friendship.requester_id == viewer_id) & (Friendship.addressee_id == user_id))
                | ((Friendship.addressee_id == viewer_id) & (Friendship.requester_id == user_id)),
            )
            .first()
            is not None
        )
        if is_friend:
            visibility_filter = or_(
                Activity.visibility == Visibility.PUBLIC,
                Activity.visibility == Visibility.FRIENDS,
            ) & (Activity.owner_id == user_id)
        else:
            visibility_filter = (Activity.visibility == Visibility.PUBLIC) & (
                Activity.owner_id == user_id
            )
    query = db.query(Activity).filter(visibility_filter)
    if sport_type:
        query = query.filter(Activity.sport_type == sport_type)
    activities = query.order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()
    return [enrich_activity(a, viewer_id) for a in activities]
