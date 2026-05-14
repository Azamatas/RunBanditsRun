from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from backend.models.activity import Activity
from backend.services.activity_service import (
    _filter_visible_activities,
    _query_activities_with_relations,
    enrich_activity,
)

logger = logging.getLogger("runbanditsrun.services.feed")


def get_feed(db: Session, viewer_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    logger.debug(f"Generating feed for user {viewer_id} with limit={limit}, offset={offset}")
    query = _query_activities_with_relations(db)
    query = _filter_visible_activities(query, viewer_id)
    activities = query.order_by(Activity.created_at.desc()).offset(offset).limit(limit).all()
    return [enrich_activity(a, viewer_id) for a in activities]
