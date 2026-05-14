import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.segment import Segment, SegmentEffort
from backend.models.user import User

logger = logging.getLogger("runbanditsrun.services.segment")


def get_segment(db: Session, segment_id: int) -> Segment | None:
    logger.debug(f"Fetching segment by ID: {segment_id}")
    return db.query(Segment).filter(Segment.id == segment_id).first()


def list_segments(db: Session, limit: int = 20, offset: int = 0) -> list[Segment]:
    logger.debug(f"Listing segments with offset={offset}, limit={limit}")
    return db.query(Segment).offset(offset).limit(limit).all()


def create_segment(db: Session, data: dict) -> Segment:
    logger.info(f"Creating segment with data: {list(data.keys())}")
    segment = Segment(**data)
    db.add(segment)
    db.commit()
    db.refresh(segment)
    logger.info(f"Created segment {segment.id}")
    return segment


def get_leaderboard(db: Session, segment_id: int, limit: int = 10) -> list[dict]:
    logger.debug(f"Generating leaderboard for segment {segment_id} with limit={limit}")
    results = (
        db.query(
            SegmentEffort.athlete_id,
            User.username,
            func.min(SegmentEffort.elapsed_time).label("best_time"),
        )
        .join(User, User.id == SegmentEffort.athlete_id)
        .filter(SegmentEffort.segment_id == segment_id)
        .group_by(SegmentEffort.athlete_id, User.username)
        .order_by(func.min(SegmentEffort.elapsed_time))
        .limit(limit)
        .all()
    )

    return [
        {
            "athlete_id": r.athlete_id,
            "athlete_name": r.username,
            "best_time": r.best_time,
            "rank": idx + 1,
        }
        for idx, r in enumerate(results)
    ]


def get_user_efforts(db: Session, segment_id: int, user_id: int) -> list[SegmentEffort]:
    logger.debug(f"Fetching efforts for user {user_id} on segment {segment_id}")
    return (
        db.query(SegmentEffort)
        .filter(
            SegmentEffort.segment_id == segment_id,
            SegmentEffort.athlete_id == user_id,
        )
        .order_by(SegmentEffort.started_at.desc())
        .all()
    )
