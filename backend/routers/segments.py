from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.segment import SegmentCreate, SegmentOut, LeaderboardEntry, SegmentEffortOut
from backend.services import segment_service
from backend.routers.deps import get_current_user

router = APIRouter(prefix="/segments", tags=["segments"])


@router.get("/", response_model=list[SegmentOut])
def list_segments(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return segment_service.list_segments(db, limit=limit, offset=offset)


@router.get("/{segment_id}", response_model=SegmentOut)
def get_segment(segment_id: int, db: Session = Depends(get_db)):
    segment = segment_service.get_segment(db, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment


@router.post("/", response_model=SegmentOut, status_code=201)
def create_segment(body: SegmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return segment_service.create_segment(db, body.model_dump())


@router.get("/{segment_id}/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(
    segment_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    segment = segment_service.get_segment(db, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment_service.get_leaderboard(db, segment_id, limit=limit)


@router.get("/{segment_id}/efforts", response_model=list[SegmentEffortOut])
def get_user_efforts(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    segment = segment_service.get_segment(db, segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment_service.get_user_efforts(db, segment_id, current_user.id)