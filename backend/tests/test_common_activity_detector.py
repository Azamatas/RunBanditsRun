import pytest
from datetime import datetime, timedelta
from sqlalchemy import text

from backend.models.activity import Activity, SportType, Visibility
from backend.models.common_activity import CommonActivity
from backend.models.user import User
from backend.jobs.common_activity_detector import detect_common_activities_job
from backend.config import config


class TestCommonActivityDetector:
    def test_detect_common_activities_job_basic(self, db):
        """Test that the job creates common activities and links activities"""
        import uuid
        user = User(username=f"testuser_{uuid.uuid4().hex[:8]}", email=f"test_{uuid.uuid4().hex[:8]}@test.com", password_hash="hash")
        db.add(user)
        db.commit()

        base_time = datetime.utcnow() - timedelta(minutes=30)
        
        activity_ids = []
        for i in range(3):
            activity = Activity(
                owner_id=user.id,
                title=f"Run {i}",
                sport_type=SportType.RUN,
                distance=1000.0,
                duration=600,
                visibility=Visibility.PUBLIC,
                started_at=base_time + timedelta(minutes=i),
                created_at=base_time + timedelta(minutes=i),
                path=text("ST_GeomFromText('LINESTRING(0 0, 0.1 0.1)', 4326)"),
                polyline=None
            )
            db.add(activity)
            db.flush()
            activity_ids.append(activity.id)
        
        db.commit()

        detect_common_activities_job()
        common_activities = db.query(CommonActivity).all()
        assert len(common_activities) == 1, f"Expected 1 common activity, got {len(common_activities)}"
        
        common_activity = common_activities[0]
        assert common_activity.sport_type == SportType.RUN
        
        linked_activities = db.query(Activity).filter(
            Activity.common_activity_id == common_activity.id
        ).all()
        assert len(linked_activities) == 3, f"Expected 3 linked activities, got {len(linked_activities)}"
        
        linked_ids = {a.id for a in linked_activities}
        assert set(activity_ids) == linked_ids, "Not all activities were linked"

    def test_detect_common_activities_job_no_clustering(self, db):
        """Test that activities that are too far apart don't get clustered"""
        import uuid
        user = User(username=f"testuser2_{uuid.uuid4().hex[:8]}", email=f"test2_{uuid.uuid4().hex[:8]}@test.com", password_hash="hash")
        db.add(user)
        db.commit()

        base_time = datetime.utcnow() - timedelta(hours=1)

        far_apart_activities = [
            ("LINESTRING(0.0 0.0, 0.1 0.1)", "Run 1"),
            ("LINESTRING(1.0 1.0, 1.1 1.1)", "Run 2"),
            ("LINESTRING(2.0 2.0, 2.1 2.1)", "Run 3"),
        ]

        for i, (geom, title) in enumerate(far_apart_activities):
            activity = Activity(
                owner_id=user.id,
                title=title,
                sport_type=SportType.RUN,
                distance=1000.0,
                duration=600,
                visibility=Visibility.PUBLIC,
                started_at=base_time + timedelta(minutes=i),
                created_at=base_time + timedelta(minutes=i),
                path=text(f"ST_GeomFromText('{geom}', 4326)"),
                polyline=None
            )
            db.add(activity)

        db.commit()

        detect_common_activities_job()

        common_activities = db.query(CommonActivity).all()
        assert len(common_activities) == 0

    def test_detect_common_activities_job_different_sports(self, db):
        """Test that activities of different sport types create separate common activities"""
        import uuid
        user = User(username=f"testuser3_{uuid.uuid4().hex[:8]}", email=f"test3_{uuid.uuid4().hex[:8]}@test.com", password_hash="hash")
        db.add(user)
        db.commit()

        base_time = datetime.utcnow() - timedelta(hours=1)

        run_ids = []
        for i in range(3):
            activity = Activity(
                owner_id=user.id,
                title=f"Run {i}",
                sport_type=SportType.RUN,
                distance=1000.0,
                duration=600,
                visibility=Visibility.PUBLIC,
                started_at=base_time + timedelta(minutes=i),
                created_at=base_time + timedelta(minutes=i),
                path=text("ST_GeomFromText('LINESTRING(0.0 0.0, 0.1 0.1)', 4326)"),
                polyline=None
            )
            db.add(activity)
            db.flush()
            run_ids.append(activity.id)

        ride_ids = []
        for i in range(3):
            activity = Activity(
                owner_id=user.id,
                title=f"Ride {i}",
                sport_type=SportType.RIDE,
                distance=2000.0,
                duration=1200,
                visibility=Visibility.PUBLIC,
                started_at=base_time + timedelta(minutes=i+10),
                created_at=base_time + timedelta(minutes=i+10),
                path=text("ST_GeomFromText('LINESTRING(0.0 0.0, 0.1 0.1)', 4326)"),
                polyline=None
            )
            db.add(activity)
            db.flush()
            ride_ids.append(activity.id)

        db.commit()

        detect_common_activities_job()

        common_activities = db.query(CommonActivity).all()
        assert len(common_activities) == 2

        sport_types = {ca.sport_type for ca in common_activities}
        assert sport_types == {SportType.RUN, SportType.RIDE}

        for ca in common_activities:
            linked = db.query(Activity).filter(Activity.common_activity_id == ca.id).all()
            assert len(linked) == 3
            if ca.sport_type == SportType.RUN:
                linked_ids = {a.id for a in linked}
                assert set(run_ids) == linked_ids
            else:
                linked_ids = {a.id for a in linked}
                assert set(ride_ids) == linked_ids

    def test_detect_common_activities_job_min_length(self, db):
        """Test that very short paths don't create common activities"""
        import uuid
        user = User(username=f"testuser4_{uuid.uuid4().hex[:8]}", email=f"test4_{uuid.uuid4().hex[:8]}@test.com", password_hash="hash")
        db.add(user)
        db.commit()

        base_time = datetime.utcnow() - timedelta(hours=1)
        for i in range(3):
            activity = Activity(
                owner_id=user.id,
                title=f"Short Run {i}",
                sport_type=SportType.RUN,
                distance=10.0,  # Very short distance
                duration=100,
                visibility=Visibility.PUBLIC,
                started_at=base_time + timedelta(minutes=i),
                created_at=base_time + timedelta(minutes=i),
                path=text("ST_GeomFromText('LINESTRING(0.0 0.0, 0.0001 0.0001)', 4326)"),
                polyline=None
            )
            db.add(activity)

        db.commit()

        detect_common_activities_job()

        common_activities = db.query(CommonActivity).all()
        assert len(common_activities) == 0

    def test_detect_common_activities_job_already_linked(self, db):
        """Test that activities already linked to common activities are not processed again"""
        import uuid
        user = User(username=f"testuser5_{uuid.uuid4().hex[:8]}", email=f"test5_{uuid.uuid4().hex[:8]}@test.com", password_hash="hash")
        db.add(user)

        common_activity = CommonActivity(
            name="Existing Path",
            distance=1000.0,
            sport_type=SportType.RUN,
            path=text("ST_GeomFromText('LINESTRING(0.0 0.0, 0.01 0.01)', 4326)"),
            polyline=None
        )
        db.add(common_activity)
        db.commit()

        base_time = datetime.utcnow() - timedelta(hours=1)

        activity_linked = Activity(
            owner_id=user.id,
            title="Linked Run",
            sport_type=SportType.RUN,
            distance=1000.0,
            duration=600,
            visibility=Visibility.PUBLIC,
            started_at=base_time,
            created_at=base_time,
            path=text("ST_GeomFromText('LINESTRING(0.0 0.0, 0.01 0.01)', 4326)"),
            polyline=None,
            common_activity_id=common_activity.id
        )
        db.add(activity_linked)

        for i in range(3):
            activity = Activity(
                owner_id=user.id,
                title=f"New Run {i}",
                sport_type=SportType.RUN,
                distance=1000.0,
                duration=600,
                visibility=Visibility.PUBLIC,
                started_at=base_time + timedelta(minutes=i+10),
                created_at=base_time + timedelta(minutes=i+10),
                path=text("ST_GeomFromText('LINESTRING(0.1 0.1, 0.11 0.11)', 4326)"),
                polyline=None
            )
            db.add(activity)

        db.commit()

        detect_common_activities_job()

        common_activities = db.query(CommonActivity).all()
        assert len(common_activities) >= 1