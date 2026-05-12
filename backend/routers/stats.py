from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.activity import SportType
from backend.schemas.stats import StatsResponse
from backend.services import stats_service
from backend.routers.deps import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/me", response_model=StatsResponse)
def my_stats(
    sport_type: Optional[SportType] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {
        "totals": stats_service.get_totals(db, current_user.id, sport_type=sport_type),
        "personal_records": stats_service.get_personal_records(db, current_user.id),
    }