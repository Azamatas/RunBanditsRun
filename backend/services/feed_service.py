from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, select
from backend.models.activity import Activity, Visibility
from backend.models.friendship import Friendship, FriendshipStatus
from backend.services.activity_service import enrich_activity


def get_feed(db: Session, viewer_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    friend_ids_subquery = select(Friendship.addressee_id).where(
        Friendship.requester_id == viewer_id,
        Friendship.status == FriendshipStatus.ACCEPTED
    ).union(
        select(Friendship.requester_id).where(
            Friendship.addressee_id == viewer_id,
            Friendship.status == FriendshipStatus.ACCEPTED
        )
    )

    activities = db.query(Activity).filter(
        or_(
            Activity.visibility == Visibility.PUBLIC,
            Activity.owner_id == viewer_id,
            and_(
                Activity.visibility == Visibility.FRIENDS,
                Activity.owner_id.in_(friend_ids_subquery)
            )
        )
    ).order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()

    return [enrich_activity(a, viewer_id) for a in activities]