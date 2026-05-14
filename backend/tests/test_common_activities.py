from backend.models.activity import Activity, SportType, Visibility
from backend.models.common_activity import CommonActivity
from backend.models.user import User


class TestListCommonActivities:
    def test_list_common_activities(self, client, db, auth_user):
        _, headers = auth_user
        ca = CommonActivity(name="Main Loop", distance=1000, sport_type=SportType.RUN)
        db.add(ca)
        db.commit()
        resp = client.get("/common-activities/", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Main Loop"

    def test_list_common_activities_empty(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/common-activities/", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_common_activities_with_sport_type_filter(self, client, db, auth_user):
        _, headers = auth_user
        ca_run = CommonActivity(name="Run Path", distance=1000, sport_type=SportType.RUN)
        ca_ride = CommonActivity(name="Ride Path", distance=2000, sport_type=SportType.RIDE)
        db.add_all([ca_run, ca_ride])
        db.commit()
        resp = client.get("/common-activities/?sport_type=run", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["sport_type"] == "run"

    def test_list_common_activities_pagination(self, client, db, auth_user):
        _, headers = auth_user
        for i in range(25):
            ca = CommonActivity(name=f"Path {i}", distance=float(i * 100), sport_type=SportType.RUN)
            db.add(ca)
        db.commit()
        resp = client.get("/common-activities/?limit=10&offset=0", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 10

        resp = client.get("/common-activities/?limit=10&offset=10", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 10


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
    def test_leaderboard_empty(self, client, db, auth_user):
        _, headers = auth_user
        ca = CommonActivity(name="Empty Path", distance=500, sport_type="run")
        db.add(ca)
        db.commit()
        resp = client.get(f"/common-activities/{ca.id}/leaderboard", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_leaderboard_with_activities(self, client, db, auth_user):
        user, headers = auth_user
        ca = CommonActivity(name="Race Path", distance=5000, sport_type="run")
        db.add(ca)
        db.commit()

        activity1 = Activity(
            owner_id=user.id,
            title="Fast Run",
            sport_type=SportType.RUN,
            distance=5000,
            duration=1200,
            visibility=Visibility.PUBLIC,
            common_activity_id=ca.id,
        )
        activity2 = Activity(
            owner_id=user.id,
            title="Slower Run",
            sport_type=SportType.RUN,
            distance=5000,
            duration=1500,
            visibility=Visibility.PUBLIC,
            common_activity_id=ca.id,
        )
        db.add_all([activity1, activity2])
        db.commit()

        resp = client.get(f"/common-activities/{ca.id}/leaderboard", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1  # Same user, grouped
        assert data[0]["best_time"] == 1200
        assert data[0]["rank"] == 1

    def test_leaderboard_multiple_users(self, client, db, auth_user, second_user):
        user, headers = auth_user
        ca = CommonActivity(name="Race Path", distance=5000, sport_type="run")
        db.add(ca)
        db.commit()

        activity1 = Activity(
            owner_id=user.id,
            title="Fast Run",
            sport_type=SportType.RUN,
            distance=5000,
            duration=1200,
            visibility=Visibility.PUBLIC,
            common_activity_id=ca.id,
        )
        activity2 = Activity(
            owner_id=second_user.id,
            title="Faster Run",
            sport_type=SportType.RUN,
            distance=5000,
            duration=1000,
            visibility=Visibility.PUBLIC,
            common_activity_id=ca.id,
        )
        db.add_all([activity1, activity2])
        db.commit()

        resp = client.get(f"/common-activities/{ca.id}/leaderboard", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["best_time"] == 1000
        assert data[0]["rank"] == 1
        assert data[1]["best_time"] == 1200
        assert data[1]["rank"] == 2

    def test_leaderboard_not_found_common_activity(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/common-activities/9999/leaderboard", headers=headers)
        assert resp.status_code == 404

    def test_leaderboard_limit(self, client, db, auth_user, second_user):
        user, headers = auth_user
        ca = CommonActivity(name="Popular Path", distance=1000, sport_type="run")
        db.add(ca)
        db.commit()

        for i in range(15):
            duration = 1000 + i * 100
            activity = Activity(
                owner_id=user.id if i % 2 == 0 else second_user.id,
                title=f"Run {i}",
                sport_type=SportType.RUN,
                distance=1000,
                duration=duration,
                visibility=Visibility.PUBLIC,
                common_activity_id=ca.id,
            )
            db.add(activity)
        db.commit()

        resp = client.get(f"/common-activities/{ca.id}/leaderboard?limit=5", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) <= 5


class TestCommonActivityModel:
    def test_common_activity_creation(self, db):
        ca = CommonActivity(name="Test Path", distance=1000, sport_type="run")
        db.add(ca)
        db.commit()
        assert ca.id is not None
        assert ca.name == "Test Path"

    def test_common_activity_with_activities(self, db):
        user = User(username="testuser", email="test@test.com", password_hash="hash")
        db.add(user)
        db.commit()

        ca = CommonActivity(name="Test Path", distance=1000, sport_type="run")
        db.add(ca)
        db.commit()

        activity = Activity(
            owner_id=user.id,
            title="Test Run",
            sport_type=SportType.RUN,
            distance=1000,
            visibility=Visibility.PUBLIC,
            common_activity_id=ca.id,
        )
        db.add(activity)
        db.commit()

        assert activity.common_activity_id == ca.id
