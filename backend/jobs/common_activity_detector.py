import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.config import config
from backend.database import SessionLocal

logger = logging.getLogger("runbanditsrun.jobs.common_activity_detector")


def detect_common_activities_job(db: Session = None):
    own_db = db is None
    if own_db:
        db = SessionLocal()

    try:
        min_activities = config.COMMON_ACTIVITY_DETECTION_MIN_ACTIVITIES
        min_length = config.COMMON_ACTIVITY_DETECTION_MIN_LENGTH
        cluster_threshold = config.COMMON_ACTIVITY_DETECTION_CLUSTER_THRESHOLD

        # Convert cluster threshold from meters to degrees (~111km/degree)
        eps_degrees = cluster_threshold / 111000.0

        # Find clusters of spatially similar recent activities using DBSCAN
        cluster_result = db.execute(text("""
            WITH recent_activities AS (
                SELECT id, sport_type, path
                FROM activities
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                  AND common_activity_id IS NULL
                  AND path IS NOT NULL
            ),
            clustered AS (
                SELECT
                    id, sport_type, path,
                    ST_ClusterDBSCAN(ST_Centroid(path), :eps_degrees, 1)
                        OVER (PARTITION BY sport_type) AS cluster_id
                FROM recent_activities
            )
            SELECT
                sport_type,
                cluster_id,
                ARRAY_AGG(id ORDER BY id) AS activity_ids
            FROM clustered
            WHERE cluster_id IS NOT NULL
            GROUP BY sport_type, cluster_id
            HAVING COUNT(*) >= :min_activities
        """), {
            "eps_degrees": eps_degrees,
            "min_activities": min_activities,
        })

        clusters = cluster_result.fetchall()
        created_count = 0

        for sport_type, cluster_id, activity_ids in clusters:
            # Insert common activity using the first activity's path as representative;
            # skip clusters whose representative path is too short.
            insert_result = db.execute(text("""
                INSERT INTO common_activities (name, polyline, path, distance, sport_type)
                SELECT
                    'Auto: ' || sport_type || ' Path',
                    ST_AsEncodedPolyline(path),
                    path,
                    ROUND(ST_Length(path::geography)),
                    sport_type
                FROM activities
                WHERE id = :representative_id
                  AND ST_Length(path::geography) > :min_length
                RETURNING id
            """), {
                "representative_id": activity_ids[0],
                "min_length": min_length,
            })

            row = insert_result.fetchone()
            if row is None:
                continue

            common_id = row[0]
            created_count += 1

            db.execute(text("""
                UPDATE activities
                SET common_activity_id = :common_id
                WHERE id = ANY(:activity_ids)
            """), {
                "common_id": common_id,
                "activity_ids": list(activity_ids),
            })

        if own_db:
            db.commit()
        logger.info(f"Created {created_count} new common activities")

    except Exception as e:
        if own_db:
            db.rollback()
        logger.error(f"Common activity detection job failed: {e}", exc_info=True)
        raise
    finally:
        if own_db:
            db.close()


scheduler = BackgroundScheduler()

if config.COMMON_ACTIVITY_DETECTION_ENABLED:
    scheduler.add_job(
        detect_common_activities_job,
        IntervalTrigger(seconds=config.COMMON_ACTIVITY_DETECTION_INTERVAL_SECONDS),
        id="auto_common_activity_detection",
        name="Detect and create common activities from recent activities",
        replace_existing=True,
    )
    logger.info(f"Common activity detection job scheduled to run every {config.COMMON_ACTIVITY_DETECTION_INTERVAL_SECONDS} seconds")
else:
    logger.info("Common activity detection job is disabled")
