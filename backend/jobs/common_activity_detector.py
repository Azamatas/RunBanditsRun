import logging
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from geoalchemy2 import Geography
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.config import config
from backend.database import SessionLocal
from backend.models.activity import Activity
from backend.models.common_activity import CommonActivity

logger = logging.getLogger("runbanditsrun.jobs.common_activity_detector")


def _find_clusters(db: Session, eps_degrees: float, min_activities: int, hours: int):
    cutoff = datetime.now(UTC) - timedelta(hours=hours)

    recent = (
        select(Activity.id, Activity.sport_type, Activity.path)
        .where(
            Activity.created_at >= cutoff,
            Activity.common_activity_id.is_(None),
            Activity.path.isnot(None),
        )
    ).cte("recent_activities")

    clustered = (
        select(
            recent.c.id,
            recent.c.sport_type,
            func.ST_ClusterDBSCAN(
                func.ST_Centroid(recent.c.path), eps_degrees, 1
            )
            .over(partition_by=recent.c.sport_type)
            .label("cluster_id"),
        )
    ).cte("clustered")

    return db.execute(
        select(
            clustered.c.sport_type,
            clustered.c.cluster_id,
            func.array_agg(clustered.c.id).label("activity_ids"),
        )
        .where(clustered.c.cluster_id.isnot(None))
        .group_by(clustered.c.sport_type, clustered.c.cluster_id)
        .having(func.count() >= min_activities)
    ).all()


def detect_common_activities_job(db: Session):
    min_activities = config.COMMON_ACTIVITY_DETECTION_MIN_ACTIVITIES
    min_length = config.COMMON_ACTIVITY_DETECTION_MIN_LENGTH
    cluster_threshold = config.COMMON_ACTIVITY_DETECTION_CLUSTER_THRESHOLD
    time_threshold_hours = config.COMMON_ACTIVITY_DETECTION_TIME_THRESHOLD_HOURS

    eps_degrees = cluster_threshold / 111000.0

    clusters = _find_clusters(db, eps_degrees, min_activities, time_threshold_hours)
    created_count = 0

    for sport_type, cluster_id, activity_ids in clusters:
        rep_query = select(
            Activity.sport_type,
            Activity.path,
            func.ST_AsEncodedPolyline(Activity.path),
            func.round(func.ST_Length(func.cast(Activity.path, Geography))),
            func.ST_Length(func.cast(Activity.path, Geography)),
        ).where(Activity.id == activity_ids[0])

        rep_row = db.execute(rep_query).first()
        if rep_row is None:
            continue

        sport_type, path, polyline, distance, length_m = rep_row
        if length_m <= min_length:
            continue

        common_activity = CommonActivity(
            name=f"Auto: {sport_type.value} Path",
            polyline=polyline,
            path=path,
            distance=distance,
            sport_type=sport_type,
        )
        db.add(common_activity)
        db.flush()
        common_id = common_activity.id
        created_count += 1

        db.query(Activity).filter(Activity.id.in_(activity_ids)).update(
            {Activity.common_activity_id: common_id}, synchronize_session=False
        )

    logger.info(f"Created {created_count} new common activities")


def _run_scheduled_job():
    db = SessionLocal()
    try:
        detect_common_activities_job(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


scheduler = BackgroundScheduler()

if config.COMMON_ACTIVITY_DETECTION_ENABLED:
    scheduler.add_job(
        _run_scheduled_job,
        IntervalTrigger(seconds=config.COMMON_ACTIVITY_DETECTION_INTERVAL_SECONDS),
        id="auto_common_activity_detection",
        name="Detect and create common activities from recent activities",
        replace_existing=True,
    )
    logger.info(f"Common activity detection job scheduled to run every {config.COMMON_ACTIVITY_DETECTION_INTERVAL_SECONDS} seconds")
else:
    logger.info("Common activity detection job is disabled")
