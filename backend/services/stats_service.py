from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.activity import Activity, SportType
from backend.models.segment import SegmentEffort


def get_totals(db: Session, user_id: int, sport_type: SportType | None = None) -> dict:
    query = db.query(
        Activity.sport_type,
        func.count(Activity.id).label("count"),
        func.sum(Activity.distance).label("total_distance"),
        func.sum(Activity.elevation).label("total_elevation"),
        func.sum(Activity.duration).label("total_duration"),
    ).filter(Activity.owner_id == user_id)
    if sport_type:
        query = query.filter(Activity.sport_type == sport_type)
    rows = query.group_by(Activity.sport_type).all()

    return {
        row.sport_type: {
            "count": row.count,
            "total_distance": row.total_distance or 0,
            "total_elevation": row.total_elevation or 0,
            "total_duration": row.total_duration or 0,
        }
        for row in rows
    }


def get_personal_records(db: Session, user_id: int) -> list[dict]:
    best = db.query(
        SegmentEffort.segment_id,
        func.min(SegmentEffort.elapsed_time).label("best_time"),
    ).filter(SegmentEffort.athlete_id == user_id).group_by(SegmentEffort.segment_id).all()

    return [{"segment_id": r.segment_id, "best_time": r.best_time} for r in best]
