from __future__ import annotations
from sqlalchemy.orm import Session, selectinload, Query
from sqlalchemy.sql.selectable import Select, CompoundSelect
from sqlalchemy import or_, and_, select
from backend.models.activity import Activity, Visibility
from backend.models.friendship import Friendship, FriendshipStatus


def _query_activities_with_relations(db: Session) -> Query[Activity]:
    """Return a query with owner and kudos eager-loaded."""
    return db.query(Activity).options(
        selectinload(Activity.owner),
        selectinload(Activity.kudos)
    )


def _get_friend_ids_subquery(viewer_id: int) -> CompoundSelect[tuple[int]]:
    """Build subquery for getting friend IDs of a user."""
    return select(Friendship.addressee_id).where(
        Friendship.requester_id == viewer_id,
        Friendship.status == FriendshipStatus.ACCEPTED
    ).union(
        select(Friendship.requester_id).where(
            Friendship.addressee_id == viewer_id,
            Friendship.status == FriendshipStatus.ACCEPTED
        )
    )


def _filter_visible_activities(query: Query[Activity], viewer_id: int) -> Query[Activity]:
    """Filter activities to only those visible to the viewer."""
    friend_ids_subquery = _get_friend_ids_subquery(viewer_id)
    return query.filter(
        or_(
            Activity.visibility == Visibility.PUBLIC,
            Activity.owner_id == viewer_id,
            and_(
                Activity.visibility == Visibility.FRIENDS,
                Activity.owner_id.in_(friend_ids_subquery)
            )
        )
    )


def _is_friend(db: Session, user_id: int, other_id: int) -> bool:
    return db.query(Friendship).filter(
        Friendship.status == FriendshipStatus.ACCEPTED,
        ((Friendship.requester_id == user_id) & (Friendship.addressee_id == other_id)) |
        ((Friendship.requester_id == other_id) & (Friendship.addressee_id == user_id))
    ).first() is not None


def can_view(db: Session, activity: Activity, viewer_id: int | None) -> bool:
    if activity.visibility == Visibility.PUBLIC:
        return True
    if viewer_id is None:
        return False
    if activity.owner_id == viewer_id:
        return True
    if activity.visibility == Visibility.FRIENDS:
        return _is_friend(db, viewer_id, activity.owner_id)
    return False


def enrich_activity(activity: Activity, user_id: int) -> dict:
    return {
        **activity.__dict__,
        "kudos_count": len(activity.kudos),
        "owner_username": activity.owner.username,
        "user_has_kudos": any(k.user_id == user_id for k in activity.kudos),
    }


def create_activity(db: Session, owner_id: int, data: dict, tagged_ids: list[int]) -> Activity:
    from backend.models.user import User
    activity = Activity(owner_id=owner_id, **data)
    if tagged_ids:
        tagged = db.query(User).filter(User.id.in_(tagged_ids)).all()
        activity.tagged_athletes = tagged
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_activity(db: Session, activity_id: int, viewer_id: int | None) -> Activity | None:
    activity = _query_activities_with_relations(db).filter(Activity.id == activity_id).first()
    if activity and can_view(db, activity, viewer_id):
        return activity
    return None


def update_activity(db: Session, activity_id: int, owner_id: int, updates: dict) -> Activity | None:
    activity = _query_activities_with_relations(db).filter(Activity.id == activity_id, Activity.owner_id == owner_id).first()
    if not activity:
        return None
    for field, value in updates.items():
        setattr(activity, field, value)
    db.commit()
    db.refresh(activity)
    return activity


def delete_activity(db: Session, activity_id: int, owner_id: int) -> bool:
    from backend.models.activity import Activity as ActivityModel
    activity = db.query(ActivityModel).filter(ActivityModel.id == activity_id, ActivityModel.owner_id == owner_id).first()
    if not activity:
        return False
    db.delete(activity)
    db.commit()
    return True


def list_activities(db: Session, viewer_id: int, sport_type=None, offset: int = 0, limit: int = 20) -> list[dict]:
    query = _query_activities_with_relations(db)
    query = _filter_visible_activities(query, viewer_id)
    if sport_type:
        query = query.filter(Activity.sport_type == sport_type)
    activities = query.order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()
    return [enrich_activity(a, viewer_id) for a in activities]