# Automatic Segment Detection Implementation Plan

## Overview
Implement a background job that periodically analyzes recent activities, clusters them by spatial proximity using PostGIS, and creates common path entries automatically.

---

## 1. Database Schema

### 1.1 Add to `backend/init_db.sql`

```sql
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Users table (existing, no changes needed)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    location VARCHAR(100),
    bio TEXT
);

-- Common activities table (replaces segments + segment_efforts)
CREATE TABLE common_activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    polyline TEXT,
    path GEOMETRY(LineString, 4326),
    distance FLOAT,
    sport_type VARCHAR(20)
);

-- Activities table with geometry and link to common_activities
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    sport_type VARCHAR(20) NOT NULL,
    distance FLOAT,
    duration INTEGER,
    elevation FLOAT,
    polyline TEXT,
    path GEOMETRY(LineString, 4326),
    visibility VARCHAR(20) DEFAULT 'public',
    started_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    common_activity_id INTEGER REFERENCES common_activities(id)
);

-- Friendships, kudos, and other existing tables remain unchanged

-- Spatial indexes
CREATE INDEX idx_activities_path ON activities USING GIST(path);
CREATE INDEX idx_common_activities_path ON common_activities USING GIST(path);

-- Function to decode polyline to geometry
CREATE OR REPLACE FUNCTION decode_polyline_to_geom(encoded TEXT)
RETURNS GEOMETRY(LineString, 4326) AS $$
  SELECT ST_LineFromEncodedPolyline(encoded);
$$ LANGUAGE SQL IMMUTABLE;

-- Trigger to auto-populate path from polyline on activities
CREATE OR REPLACE FUNCTION update_activity_path()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.polyline IS NOT NULL THEN
    NEW.path := decode_polyline_to_geom(NEW.polyline);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_activity_path
BEFORE INSERT OR UPDATE ON activities
FOR EACH ROW EXECUTE FUNCTION update_activity_path();

-- Trigger to auto-populate path from polyline on common_activities
CREATE OR REPLACE FUNCTION update_common_activity_path()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.polyline IS NOT NULL THEN
    NEW.path := decode_polyline_to_geom(NEW.polyline);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_common_activity_path
BEFORE INSERT OR UPDATE ON common_activities
FOR EACH ROW EXECUTE FUNCTION update_common_activity_path();
```

---

## 2. Backend Changes

### 2.1 New Dependencies

```bash
pip install apscheduler geoalchemy2
```

### 2.2 New Files

#### `backend/jobs/__init__.py`
```python
from backend.jobs.segment_detector import scheduler
```

#### `backend/jobs/segment_detector.py`
```python
import logging
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database import SessionLocal

logger = logging.getLogger("runbanditsrun.jobs.segment_detector")


def detect_segments_job():
    db: Session = SessionLocal()
    try:
        # Step 1: Find recent activities not linked to common_activities
        # Step 2: Cluster by spatial proximity
        # Step 3: Create new common_activities from clusters
        # Step 4: Link activities to new common_activities

        result = db.execute(text("""
            WITH
            -- Recent activities (last 24h) not yet linked to common paths
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
            ),

            -- Cluster activities by sport type and spatial proximity (50m threshold)
            clusters AS (
                SELECT
                    sport_type,
                    ST_ClusterWithin(path, 50) AS cluster_geom,
                    COUNT(*) AS activity_count,
                    ARRAY_AGG(id) AS activity_ids
                FROM recent_activities
                GROUP BY sport_type, ST_ClusterWithin(path, 50)
                HAVING COUNT(*) >= 3
            ),

            -- Extract common path from each cluster
            common_paths AS (
                SELECT
                    sport_type,
                    ST_LineMerge(ST_Collect(cluster_geom)) AS merged_path,
                    ARRAY_AGG(DISTINCT unnest(activity_ids)) AS activity_ids
                FROM clusters
                GROUP BY sport_type, ST_LineMerge(ST_Collect(cluster_geom))
            )

            -- Insert new common_activities
            INSERT INTO common_activities (name, polyline, path, distance, sport_type)
            SELECT
                'Auto: ' || sport_type || ' Path ' || row_number() OVER (),
                ST_AsEncodedPolyline(merged_path),
                merged_path,
                ROUND(ST_Length(merged_path::geography)),
                sport_type
            FROM common_paths
            WHERE ST_Length(merged_path::geography) > 100  -- Minimum 100m
            ON CONFLICT (polyline) DO NOTHING
            RETURNING id, ARRAY_AGG(DISTINCT unnest(activity_ids)) AS activity_ids
        """))

        new_common_activities = result.fetchall()

        # Step 4: Link activities to new common_activities
        for common_id, activity_ids in new_common_activities:
            db.execute(
                text("""
                    UPDATE activities
                    SET common_activity_id = :common_id
                    WHERE id = ANY(:activity_ids)
                """),
                {"common_id": common_id, "activity_ids": activity_ids}
            )

        db.commit()
        logger.info(f"Created {len(new_common_activities)} new common activities")

    except Exception as e:
        db.rollback()
        logger.error(f"Segment detection job failed: {e}", exc_info=True)
        raise
    finally:
        db.close()


# Initialize scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()
scheduler.add_job(
    detect_segments_job,
    IntervalTrigger(hours=24),
    id="auto_segment_detection",
    name="Detect and create common activities from recent activities",
    replace_existing=True,
)
```

### 2.3 Modified Files

#### `backend/main.py`

Add after app creation:
```python
from backend.jobs.segment_detector import scheduler

# Start the scheduler
scheduler.start()

# Shutdown hook
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
```

#### `backend/database.py`
No changes needed - SessionLocal already exists.

#### `backend/models/activity.py`
Add geometry import and path field:
```python
from geoalchemy2 import Geometry

class Activity(Base):
    # ... existing fields ...
    path: Mapped[Any] = mapped_column(Geometry(geometry_type='LINESTRING', srid=4326))
    common_activity_id: Mapped[int | None] = mapped_column(ForeignKey("common_activities.id"))
    
    common_activity: Mapped["CommonActivity"] = relationship("CommonActivity", back_populates="activities")
```

#### `backend/models/__init__.py`
Add CommonActivity to exports.

#### `backend/models/common_activity.py` (NEW)
```python
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from geoalchemy2 import Geometry

from backend.database import Base

if TYPE_CHECKING:
    from backend.models.activity import Activity


class CommonActivity(Base):
    __tablename__ = "common_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    polyline: Mapped[str | None] = mapped_column(Text)
    path: Mapped[Any] = mapped_column(Geometry(geometry_type='LINESTRING', srid=4326))
    distance: Mapped[float | None] = mapped_column(Float)
    sport_type: Mapped[str | None] = mapped_column(String(20))

    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="common_activity")
```

---

## 3. Frontend Changes

### 3.1 API Changes

#### `frontend/src/api/segments.js` → `frontend/src/api/commonActivities.js`
```javascript
import client from "./client";

export const getCommonActivities = () => client.get("/common-activities/").then((r) => r.data);
export const getCommonActivity = (id) => client.get(`/common-activities/${id}`).then((r) => r.data);
export const getCommonActivityLeaderboard = (id) => client.get(`/common-activities/${id}/leaderboard`).then((r) => r.data);
```

### 3.2 Router Changes

#### `backend/routers/segments.py` → `backend/routers/common_activities.py`
```python
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.routers.deps import get_current_user
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
    return common_activity_service.list_common_activities(db, sport_type=sport_type, limit=limit, offset=offset)


@router.get("/{common_activity_id}", response_model=CommonActivityOut)
def get_common_activity(common_activity_id: int, db: Session = Depends(get_db)):
    common_activity = common_activity_service.get_common_activity(db, common_activity_id)
    if not common_activity:
        raise HTTPException(status_code=404, detail="Common activity not found")
    return common_activity


@router.get("/{common_activity_id}/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(
    common_activity_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    common_activity = common_activity_service.get_common_activity(db, common_activity_id)
    if not common_activity:
        raise HTTPException(status_code=404, detail="Common activity not found")
    return common_activity_service.get_leaderboard(db, common_activity_id, limit=limit)
```

### 3.3 Schema Changes

#### `backend/schemas/common_activity.py` (NEW)
```python
from datetime import datetime

from pydantic import BaseModel


class CommonActivityOut(BaseModel):
    id: int
    name: str
    polyline: str | None
    distance: float | None
    sport_type: str | None


class LeaderboardEntry(BaseModel):
    athlete_id: int
    athlete_name: str
    best_time: int
    rank: int
```

---

## 4. Service Layer

### 4.1 New File: `backend/services/common_activity_service.py`
```python
import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.common_activity import CommonActivity
from backend.models.user import User

logger = logging.getLogger("runbanditsrun.services.common_activity")


def get_common_activity(db: Session, common_activity_id: int) -> CommonActivity | None:
    logger.debug(f"Fetching common activity by ID: {common_activity_id}")
    return db.query(CommonActivity).filter(CommonActivity.id == common_activity_id).first()


def list_common_activities(
    db: Session,
    sport_type: str | None = None,
    limit: int = 20,
    offset: int = 0
) -> list[CommonActivity]:
    logger.debug(f"Listing common activities with offset={offset}, limit={limit}")
    query = db.query(CommonActivity).offset(offset).limit(limit)
    if sport_type:
        query = query.filter(CommonActivity.sport_type == sport_type)
    return query.all()


def get_leaderboard(db: Session, common_activity_id: int, limit: int = 10) -> list[dict]:
    logger.debug(f"Generating leaderboard for common activity {common_activity_id} with limit={limit}")
    results = (
        db.query(
            User.id.label("athlete_id"),
            User.username.label("athlete_name"),
            func.min(CommonActivityActivities.elapsed_time).label("best_time"),
        )
        .join(User, User.id == CommonActivityActivities.athlete_id)
        .filter(CommonActivityActivities.common_activity_id == common_activity_id)
        .group_by(User.id, User.username)
        .order_by(func.min(CommonActivityActivities.elapsed_time))
        .limit(limit)
        .all()
    )

    return [
        {
            "athlete_id": r.athlete_id,
            "athlete_name": r.athlete_name,
            "best_time": r.best_time,
            "rank": idx + 1,
        }
        for idx, r in enumerate(results)
    ]
```

Note: You'll need a SQLAlchemy model for the many-to-many relationship or use raw SQL for leaderboard.

---

## 5. Configuration

### `backend/config.py`

Add configuration for the job:
```python
# Segment detection job settings
SEGMENT_DETECTION_ENABLED = os.getenv("SEGMENT_DETECTION_ENABLED", "true").lower() == "true"
SEGMENT_DETECTION_INTERVAL_HOURS = int(os.getenv("SEGMENT_DETECTION_INTERVAL_HOURS", "24"))
SEGMENT_DETECTION_CLUSTER_THRESHOLD_METERS = float(os.getenv("SEGMENT_DETECTION_CLUSTER_THRESHOLD", "50.0"))
SEGMENT_DETECTION_MIN_ACTIVITIES = int(os.getenv("SEGMENT_DETECTION_MIN_ACTIVITIES", "3"))
SEGMENT_DETECTION_MIN_LENGTH_METERS = float(os.getenv("SEGMENT_DETECTION_MIN_LENGTH", "100.0"))
```

---

## 6. Testing

### `backend/tests/test_common_activities.py` (NEW)
```python
from backend.models.activity import Activity, SportType, Visibility
from backend.models.common_activity import CommonActivity


class TestListCommonActivities:
    def test_list_common_activities(self, client, db, auth_user):
        _, headers = auth_user
        db.add(CommonActivity(name="Main Loop", distance=1000, sport_type="run"))
        db.commit()
        resp = client.get("/common-activities/", headers=headers)
        assert resp.status_code == 200

    def test_list_common_activities_empty(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/common-activities/", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetCommonActivity:
    def test_get_common_activity(self, client, db, auth_user):
        _, headers = auth_user
        ca = CommonActivity(name="Main Loop", distance=1000, sport_type="run")
        db.add(ca)
        db.commit()
        resp = client.get(f"/common-activities/{ca.id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Main Loop"

    def test_get_common_activity_not_found(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/common-activities/9999", headers=headers)
        assert resp.status_code == 404


class TestLeaderboard:
    def test_leaderboard(self, client, db, auth_user):
        user, headers = auth_user
        ca = CommonActivity(name="Hill Sprint", distance=500, sport_type="run")
        activity = Activity(
            owner_id=user.id,
            title="Test Run",
            sport_type=SportType.RUN,
            visibility=Visibility.PUBLIC,
        )
        db.add(ca)
        db.add(activity)
        db.commit()
        # Need to set common_activity_id and create effort record
        # This would need additional setup for the new model
        resp = client.get(f"/common-activities/{ca.id}/leaderboard", headers=headers)
        assert resp.status_code == 200


class TestSegmentDetectionJob:
    def test_detect_segments_job_creates_common_activities(self, db):
        # Insert test activities with similar paths
        # Call detect_segments_job()
        # Assert new common_activities were created
        pass

    def test_detect_segments_job_links_activities(self, db):
        # Insert test activities
        # Call detect_segments_job()
        # Assert activities.common_activity_id is set
        pass
```

---

## 7. Deployment Notes

### Environment Variables

```bash
# Enable/disable the job
SEGMENT_DETECTION_ENABLED=true

# Job frequency (hours)
SEGMENT_DETECTION_INTERVAL_HOURS=24

# Clustering parameters
SEGMENT_DETECTION_CLUSTER_THRESHOLD=50.0    # meters
SEGMENT_DETECTION_MIN_ACTIVITIES=3         # minimum activities per cluster
SEGMENT_DETECTION_MIN_LENGTH=100.0          # minimum segment length in meters
```

### Production Considerations

1. **APScheduler in production**: Use `apscheduler.jobstores.sqlalchemy` for job persistence across restarts
2. **Time zones**: Ensure scheduler uses UTC
3. **Locking**: Add row-level locking for concurrent job runs
4. **Monitoring**: Log job duration and results count
5. **Error handling**: Notify on repeated failures

### Scaling

For high-volume sites:
- Switch to Celery + Redis for distributed task queue
- Run clustering job more frequently (hourly)
- Partition activities by date for faster queries

---

## 8. File Checklist

| File | Status | Action |
|------|--------|--------|
| `backend/init_db.sql` | NEW | Replace existing |
| `backend/jobs/__init__.py` | NEW | Create |
| `backend/jobs/segment_detector.py` | NEW | Create |
| `backend/main.py` | MODIFY | Add scheduler start/shutdown |
| `backend/config.py` | MODIFY | Add job settings |
| `backend/models/common_activity.py` | NEW | Create |
| `backend/models/activity.py` | MODIFY | Add path, common_activity_id |
| `backend/services/common_activity_service.py` | NEW | Create |
| `backend/routers/common_activities.py` | NEW | Create |
| `backend/schemas/common_activity.py` | NEW | Create |
| `backend/tests/test_common_activities.py` | NEW | Create |
| `frontend/src/api/commonActivities.js` | NEW | Create |

---

## 9. Implementation Order

1. **Database**: Update `init_db.sql` and recreate test database
2. **Backend Models**: Create `common_activity.py`, modify `activity.py`
3. **Backend Config**: Add environment variables
4. **Backend Services**: Create `common_activity_service.py`
5. **Backend Job**: Create `segment_detector.py` and `jobs/__init__.py`
6. **Backend Main**: Add scheduler startup/shutdown
7. **Backend Router**: Create `common_activities.py`
8. **Backend Schemas**: Create `common_activity.py`
9. **Frontend API**: Create `commonActivities.js`
10. **Tests**: Create `test_common_activities.py`
11. **Manual Test**: Run job and verify common activities created
