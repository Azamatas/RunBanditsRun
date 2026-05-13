from sqlalchemy.orm import Session
from sqlalchemy import or_, select
from backend.models.user import User
from backend.models.friendship import Friendship, FriendshipStatus
from backend.models.activity import Activity, Visibility
from backend.services import auth_service


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, current_user: User, updates: dict) -> User:
    if "username" in updates and updates["username"] != current_user.username:
        existing = auth_service.get_user_by_username(db, updates["username"])
        if existing:
            raise ValueError("Username already taken")
    for field, value in updates.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


def get_followers(db: Session, user_id: int) -> list[User]:
    requester_ids = select(Friendship.requester_id).where(
        Friendship.addressee_id == user_id,
        Friendship.status == FriendshipStatus.ACCEPTED
    )
    return db.query(User).filter(User.id.in_(requester_ids)).all()


def get_following(db: Session, user_id: int) -> list[User]:
    addressee_ids = select(Friendship.addressee_id).where(
        Friendship.requester_id == user_id,
        Friendship.status == FriendshipStatus.ACCEPTED
    )
    return db.query(User).filter(User.id.in_(addressee_ids)).all()


def get_pending_requests(db: Session, user_id: int) -> list[User]:
    requester_ids = select(Friendship.requester_id).where(
        Friendship.addressee_id == user_id,
        Friendship.status == FriendshipStatus.PENDING
    )
    return db.query(User).filter(User.id.in_(requester_ids)).all()


def get_pending_requests_detailed(db: Session, user_id: int) -> list[dict]:
    from backend.schemas.user import UserOut
    friendships = db.query(Friendship).filter(
        Friendship.addressee_id == user_id,
        Friendship.status == FriendshipStatus.PENDING
    ).all()
    return [
        {
            "id": f.id,
            "requester_id": f.requester_id,
            "requester": UserOut.model_validate(db.query(User).filter(User.id == f.requester_id).first()),
            "status": f.status.value,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in friendships
    ]


def get_sent_requests(db: Session, user_id: int) -> list[dict]:
    friendships = db.query(Friendship).filter(
        Friendship.requester_id == user_id,
        Friendship.status == FriendshipStatus.PENDING
    ).all()
    return [{"id": f.id, "addressee_id": f.addressee_id, "status": f.status.value} for f in friendships]


def search_users(db: Session, current_user_id: int, query: str = "", limit: int = 50) -> list[User]:
    q = db.query(User).filter(User.id != current_user_id)
    if query:
        q = q.filter(User.username.ilike(f"%{query}%"))
    return q.limit(limit).all()


def follow_user(db: Session, current_user_id: int, target_user_id: int) -> str:
    if current_user_id == target_user_id:
        raise ValueError("Cannot follow yourself")
    existing = db.query(Friendship).filter(
        Friendship.requester_id == current_user_id,
        Friendship.addressee_id == target_user_id
    ).first()
    if existing:
        raise ValueError("Request already sent")
    db.add(Friendship(requester_id=current_user_id, addressee_id=target_user_id))
    db.commit()
    return "pending"


def accept_follow(db: Session, current_user_id: int, requester_id: int) -> str:
    friendship = db.query(Friendship).filter(
        Friendship.requester_id == requester_id,
        Friendship.addressee_id == current_user_id,
        Friendship.status == FriendshipStatus.PENDING
    ).first()
    if not friendship:
        raise LookupError("No pending request")
    friendship.status = FriendshipStatus.ACCEPTED
    db.commit()
    return "accepted"


def unfollow_user(db: Session, current_user_id: int, target_user_id: int) -> None:
    friendship = db.query(Friendship).filter(
        ((Friendship.requester_id == current_user_id) & (Friendship.addressee_id == target_user_id)) |
        ((Friendship.addressee_id == current_user_id) & (Friendship.requester_id == target_user_id))
    ).first()
    if not friendship:
        raise LookupError("No friendship found")
    db.delete(friendship)
    db.commit()


def get_user_activities(db: Session, user_id: int, viewer_id: int, sport_type=None, offset: int = 0, limit: int = 20) -> list[dict] | None:
    from backend.services.activity_service import enrich_activity
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        return None
    if user_id == viewer_id:
        visibility_filter = Activity.owner_id == viewer_id
    else:
        is_friend = db.query(Friendship).filter(
            Friendship.status == FriendshipStatus.ACCEPTED,
            ((Friendship.requester_id == viewer_id) & (Friendship.addressee_id == user_id)) |
            ((Friendship.addressee_id == viewer_id) & (Friendship.requester_id == user_id))
        ).first() is not None
        if is_friend:
            visibility_filter = or_(
                Activity.visibility == Visibility.PUBLIC,
                Activity.visibility == Visibility.FRIENDS,
            ) & (Activity.owner_id == user_id)
        else:
            visibility_filter = (Activity.visibility == Visibility.PUBLIC) & (Activity.owner_id == user_id)
    query = db.query(Activity).filter(visibility_filter)
    if sport_type:
        query = query.filter(Activity.sport_type == sport_type)
    activities = query.order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()
    return [enrich_activity(a, viewer_id) for a in activities]