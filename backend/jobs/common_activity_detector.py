import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.config import config
from backend.database import SessionLocal

logger = logging.getLogger("runbanditsrun.jobs.common_activity_detector")


def detect_common_activities_job():
    db: Session = SessionLocal()
    try:
        cluster_threshold = config.COMMON_ACTIVITY_DETECTION_CLUSTER_THRESHOLD
        min_activities = config.COMMON_ACTIVITY_DETECTION_MIN_ACTIVITIES
        min_length = config.COMMON_ACTIVITY_DETECTION_MIN_LENGTH



        # Debug: Check paths
        debug_result = db.execute(text("""
            SELECT id, sport_type, ST_AsText(path), ST_IsValid(path), ST_Length(path::geography)
            FROM activities
            WHERE created_at >= NOW() - INTERVAL '24 hours'
              AND common_activity_id IS NULL
              AND path IS NOT NULL
        """))
        for row in debug_result:
            logger.info(f"Activity {row[0]}: sport={row[1]}, path={row[2]}, valid={row[3]}, length={row[4]}")

        result = db.execute(text("""
            WITH
            recent_activities AS (
                SELECT
                    id,
                    owner_id,
                    sport_type,
                    path,
                    polyline,
                    distance,
                    started_at
                FROM activities
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                  AND common_activity_id IS NULL
                  AND path IS NOT NULL
            ),

            clusters AS (
                SELECT
                    sport_type,
                    ARRAY_AGG(id) AS activity_ids,
                    MAX(path) AS merged_path
                FROM recent_activities
                GROUP BY sport_type
                HAVING COUNT(*) >= :min_activities AND ST_Length(MAX(path)::geography) > :min_length
            )

            INSERT INTO common_activities (name, polyline, path, distance, sport_type)
            SELECT
                'Auto: ' || sport_type || ' Path ' || row_number() OVER (),
                ST_AsEncodedPolyline(merged_path),
                merged_path,
                ROUND(ST_Length(merged_path::geography)),
                sport_type
            FROM clusters
            RETURNING id, sport_type, path AS merged_path
        """), {"cluster_threshold": cluster_threshold, "min_activities": min_activities, "min_length": min_length})

        new_common_activities = result.fetchall()

        for common_id, sport_type, common_path in new_common_activities:
            db.execute(text("""
                UPDATE activities
                SET common_activity_id = :common_id
                WHERE sport_type = :sport_type
                  AND common_activity_id IS NULL
                  AND created_at >= NOW() - INTERVAL '24 hours'
            """), {
                "common_id": common_id,
                "sport_type": sport_type
            })

        db.commit()
        logger.info(f"Created {len(new_common_activities)} new common activities")

    except Exception as e:
        db.rollback()
        logger.error(f"Common activity detection job failed: {e}", exc_info=True)
        raise
    finally:
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
