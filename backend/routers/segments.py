import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.routers.deps import get_current_user
from backend.schemas.segment import LeaderboardEntry, SegmentCreate, SegmentEffortOut, SegmentOut
from backend.services import segment_service

logger = logging.getLogger("runbanditsrun.routers.segments")

router = APIRouter(prefix="/segments", tags=["segments"])


@router.get("/", response_model=list[SegmentOut])
def list_segments(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    logger.debug(f"Listing segments with offset={offset}, limit={limit}")
    return segment_service.list_segments(db, limit=limit, offset=offset)


@router.get("/{segment_id}", response_model=SegmentOut)
def get_segment(segment_id: int, db: Session = Depends(get_db)):
    logger.debug(f"Requested segment: {segment_id}")
    segment = segment_service.get_segment(db, segment_id)
    if not segment:
        logger.warning(f"Segment {segment_id} not found")
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment


@router.post("/", response_model=SegmentOut, status_code=201)
def create_segment(
    body: SegmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"User {current_user.id} creating segment")
    segment = segment_service.create_segment(db, body.model_dump())
    logger.info(f"User {current_user.id} created segment {segment.id}")
    return segment


@router.get("/{segment_id}/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(
    segment_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    logger.debug(f"Requested leaderboard for segment {segment_id} with limit={limit}")
    segment = segment_service.get_segment(db, segment_id)
    if not segment:
        logger.warning(f"Segment {segment_id} not found when fetching leaderboard")
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment_service.get_leaderboard(db, segment_id, limit=limit)


@router.get("/{segment_id}/efforts", response_model=list[SegmentEffortOut])
def get_user_efforts(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(f"User {current_user.id} requested efforts for segment {segment_id}")
    segment = segment_service.get_segment(db, segment_id)
    if not segment:
        logger.warning(f"Segment {segment_id} not found when fetching user efforts")
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment_service.get_user_efforts(db, segment_id, current_user.id)
