import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.common_activity import CommonActivityOut, LeaderboardEntry
from backend.services import common_activity_service

logger = logging.getLogger("runbanditsrun.routers.common_activities")

router = APIRouter(prefix="/common-activities", tags=["common_activities"])


@router.get("/", response_model=list[CommonActivityOut])
def list_common_activities(
    sport_type: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    logger.debug(f"Listing common activities with offset={offset}, limit={limit}")
    return common_activity_service.list_common_activities(db, sport_type=sport_type, limit=limit, offset=offset)


@router.get("/{common_activity_id}", response_model=CommonActivityOut)
def get_common_activity(common_activity_id: int, db: Session = Depends(get_db)):
    logger.debug(f"Requested common activity: {common_activity_id}")
    common_activity = common_activity_service.get_common_activity(db, common_activity_id)
    if not common_activity:
        logger.warning(f"Common activity {common_activity_id} not found")
        raise HTTPException(status_code=404, detail="Common activity not found")
    return common_activity


@router.get("/{common_activity_id}/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(
    common_activity_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    logger.debug(f"Requested leaderboard for common activity {common_activity_id} with limit={limit}")
    common_activity = common_activity_service.get_common_activity(db, common_activity_id)
    if not common_activity:
        logger.warning(f"Common activity {common_activity_id} not found when fetching leaderboard")
        raise HTTPException(status_code=404, detail="Common activity not found")
    return common_activity_service.get_leaderboard(db, common_activity_id, limit=limit)
