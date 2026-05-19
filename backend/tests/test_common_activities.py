from sqlalchemy import text

from backend.models.activity import Activity, SportType, Visibility
from backend.models.common_activity import CommonActivity
from backend.models.user import User

_CLUSTER_WKT = "LINESTRING(0 0, 0.001 0.0005, 0.002 0.001, 0.003 0.0015, 0.004 0.002)"
_CLUSTER_WKT_NEAR = "LINESTRING(0 0.0001, 0.001 0.0006, 0.002 0.0011, 0.003 0.0016, 0.004 0.0021)"
_FAR_WKT = "LINESTRING(1 1, 1.001 1.0005, 1.002 1.001, 1.003 1.0015, 1.004 1.002)"


def _make_path(wkt: str):
    return text(f"ST_Transform(ST_GeomFromText('{wkt}', 4326), 3857)")


def _encode_polyline(db, wkt: str) -> str:
    return db.scalar(  # type: ignore[no-any-return]
        text(f"SELECT ST_AsEncodedPolyline(ST_GeomFromText('{wkt}', 4326))")
    )


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
        assert len(data) == 1
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


class TestCreateCommonActivity:
    def test_create_success(self, client, db, auth_user):
        _, headers = auth_user
        poly = _encode_polyline(db, _CLUSTER_WKT)
        body = {"name": "Morning Loop", "sport_type": "run", "polyline": poly}
        resp = client.post("/common-activities/", json=body, headers=headers)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["name"] == "Morning Loop"
        assert data["sport_type"] == "run"
        assert data["id"] is not None

    def test_create_unauthorized(self, client):
        body = {"name": "Loop", "sport_type": "run", "polyline": "abc"}
        resp = client.post("/common-activities/", json=body)
        assert resp.status_code == 401

    def test_create_rejects_too_close(self, client, db, auth_user):
        _, headers = auth_user
        poly = _encode_polyline(db, _CLUSTER_WKT)
        ca = CommonActivity(
            name="Existing Loop",
            sport_type=SportType.RUN,
            path=_make_path(_CLUSTER_WKT),
        )
        db.add(ca)
        db.commit()

        body = {"name": "Duplicate Loop", "sport_type": "run", "polyline": poly}
        resp = client.post("/common-activities/", json=body, headers=headers)
        assert resp.status_code == 409
        assert "similar route" in resp.json()["detail"].lower()

    def test_create_with_different_sport_not_rejected(self, client, db, auth_user):
        _, headers = auth_user
        poly_run = _encode_polyline(db, _CLUSTER_WKT)
        ca = CommonActivity(
            name="Existing Run Loop",
            sport_type=SportType.RUN,
            path=_make_path(_CLUSTER_WKT),
        )
        db.add(ca)
        db.commit()

        body = {"name": "Ride Loop", "sport_type": "ride", "polyline": poly_run}
        resp = client.post("/common-activities/", json=body, headers=headers)
        assert resp.status_code == 201, resp.text

    def test_create_links_existing_activities(self, client, db, auth_user, second_user):
        user, headers = auth_user
        poly = _encode_polyline(db, _CLUSTER_WKT)

        activity = Activity(
            owner_id=user.id,
            title="Morning Run",
            sport_type=SportType.RUN,
            distance=5000,
            duration=600,
            visibility=Visibility.PUBLIC,
            path=_make_path(_CLUSTER_WKT_NEAR),
        )
        db.add(activity)
        db.commit()

        body = {"name": "New Loop", "sport_type": "run", "polyline": poly}
        resp = client.post("/common-activities/", json=body, headers=headers)
        assert resp.status_code == 201, resp.text
        ca_id = resp.json()["id"]

        db.refresh(activity)
        assert activity.common_activity_id == ca_id

    def test_create_does_not_link_far_activities(self, client, db, auth_user, second_user):
        user, headers = auth_user
        poly = _encode_polyline(db, _CLUSTER_WKT)

        activity = Activity(
            owner_id=user.id,
            title="Far Run",
            sport_type=SportType.RUN,
            distance=5000,
            duration=600,
            visibility=Visibility.PUBLIC,
            path=_make_path(_FAR_WKT),
        )
        db.add(activity)
        db.commit()

        body = {"name": "New Loop", "sport_type": "run", "polyline": poly}
        resp = client.post("/common-activities/", json=body, headers=headers)
        assert resp.status_code == 201, resp.text

        db.refresh(activity)
        assert activity.common_activity_id is None

    def test_create_empty_polyline_rejected(self, client, auth_user):
        _, headers = auth_user
        body = {"name": "Bad", "sport_type": "run", "polyline": ""}
        resp = client.post("/common-activities/", json=body, headers=headers)
        assert resp.status_code == 422


class TestActivityAutoLink:
    def test_new_activity_auto_links_to_common(self, client, db, auth_user):
        user, headers = auth_user
        ca = CommonActivity(
            name="Morning Loop",
            sport_type=SportType.RUN,
            path=_make_path(_CLUSTER_WKT),
        )
        db.add(ca)
        db.commit()

        poly = _encode_polyline(db, _CLUSTER_WKT_NEAR)
        activity_body = {
            "title": "My Run",
            "sport_type": "run",
            "distance": 5000,
            "duration": 1800,
            "visibility": "public",
            "polyline": poly,
        }
        resp = client.post("/activities/", json=activity_body, headers=headers)
        assert resp.status_code == 200, resp.text
        activity_id = resp.json()["id"]

        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        assert activity is not None
        assert activity.common_activity_id == ca.id

    def test_new_activity_far_from_common_not_linked(self, client, db, auth_user):
        user, headers = auth_user
        ca = CommonActivity(
            name="Far Loop",
            sport_type=SportType.RUN,
            path=_make_path(_FAR_WKT),
        )
        db.add(ca)
        db.commit()

        poly = _encode_polyline(db, _CLUSTER_WKT)
        activity_body = {
            "title": "My Run",
            "sport_type": "run",
            "distance": 5000,
            "duration": 1800,
            "visibility": "public",
            "polyline": poly,
        }
        resp = client.post("/activities/", json=activity_body, headers=headers)
        assert resp.status_code == 200, resp.text
        activity_id = resp.json()["id"]

        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        assert activity is not None
        assert activity.common_activity_id is None
