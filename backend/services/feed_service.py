from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, select
from backend.models.activity import Activity, Visibility
from backend.models.friendship import Friendship, FriendshipStatus
from backend.services.activity_service import enrich_activity, _filter_visible_activities, _query_activities_with_relations


def get_feed(db: Session, viewer_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    query = _query_activities_with_relations(db)
    query = _filter_visible_activities(query, viewer_id)
    activities = query.order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()
    return [enrich_activity(a, viewer_id) for a in activities]