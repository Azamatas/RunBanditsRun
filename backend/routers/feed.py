import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.routers.deps import get_current_user
from backend.schemas.activity import ActivityOut
from backend.services import feed_service

logger = logging.getLogger("runbanditsrun.routers.feed")

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/", response_model=list[ActivityOut])
def get_feed(
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug(f"User {current_user.id} fetching feed with limit={limit}, offset={offset}")
    return feed_service.get_feed(db, current_user.id, limit, offset)
