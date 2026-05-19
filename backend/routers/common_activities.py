import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.routers.deps import get_current_user
from backend.schemas.common_activity import (
    CommonActivityCreate,
    CommonActivityOut,
    LeaderboardEntry,
)
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
    logger.debug("Listing common activities with offset=%d, limit=%d", offset, limit)
    return common_activity_service.list_common_activities(
        db, sport_type=sport_type, limit=limit, offset=offset
    )


@router.post("/", response_model=CommonActivityOut, status_code=201)
def create_common_activity(
    body: CommonActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info("User %d creating common activity", current_user.id)
    ca = common_activity_service.create_common_activity(
        db, body.model_dump()
    )
    logger.info("User %d created common activity %d", current_user.id, ca.id)
    return ca


@router.get("/{common_activity_id}", response_model=CommonActivityOut)
def get_common_activity(common_activity_id: int, db: Session = Depends(get_db)):
    logger.debug("Requested common activity: %d", common_activity_id)
    result = common_activity_service.get_common_activity(db, common_activity_id)
    if not result:
        logger.warning("Common activity %d not found", common_activity_id)
        raise HTTPException(status_code=404, detail="Common activity not found")
    return result


@router.get("/{common_activity_id}/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(
    common_activity_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    logger.debug(
        "Requested leaderboard for common activity %d with limit=%d",
        common_activity_id,
        limit,
    )
    exists = common_activity_service.get_common_activity(db, common_activity_id)
    if not exists:
        logger.warning(
            "Common activity %d not found when fetching leaderboard", common_activity_id
        )
        raise HTTPException(status_code=404, detail="Common activity not found")
    return common_activity_service.get_leaderboard(db, common_activity_id, limit=limit)
