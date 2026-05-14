from backend.models.activity import Activity, SportType, Visibility
from backend.models.segment import Segment, SegmentEffort


class TestListSegments:
    def test_list_segments(self, client, db, auth_user):
        _, headers = auth_user
        db.add(Segment(name="Main Hill", distance=1000))
        db.commit()
        resp = client.get("/segments/", headers=headers)
        assert resp.status_code == 200

    def test_list_segments_empty(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/segments/", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetSegment:
    def test_get_segment(self, client, db, auth_user):
        _, headers = auth_user
        segment = Segment(name="Main Hill", distance=1000)
        db.add(segment)
        db.commit()
        resp = client.get(f"/segments/{segment.id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Main Hill"

    def test_get_segment_not_found(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/segments/9999", headers=headers)
        assert resp.status_code == 404


class TestCreateSegment:
    def test_create_segment(self, client, auth_user):
        _, headers = auth_user
        resp = client.post(
            "/segments/", json={"name": "New Segment", "distance": 1500}, headers=headers
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "New Segment"


class TestLeaderboard:
    def test_leaderboard(self, client, db, auth_user):
        user, headers = auth_user
        segment = Segment(name="Hill Sprint", distance=500)
        activity = Activity(
            owner_id=user.id,
            title="Test Run",
            sport_type=SportType.RUN,
            visibility=Visibility.PUBLIC,
        )
        db.add(segment)
        db.add(activity)
        db.commit()
        effort = SegmentEffort(
            segment_id=segment.id, activity_id=activity.id, athlete_id=user.id, elapsed_time=120
        )
        db.add(effort)
        db.commit()
        resp = client.get(f"/segments/{segment.id}/leaderboard", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["athlete_name"] == "testuser"

    def test_leaderboard_segment_not_found(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/segments/9999/leaderboard", headers=headers)
        assert resp.status_code == 404


class TestUserEfforts:
    def test_user_efforts(self, client, db, auth_user):
        user, headers = auth_user
        segment = Segment(name="Hill Sprint", distance=500)
        activity = Activity(
            owner_id=user.id,
            title="Test Run",
            sport_type=SportType.RUN,
            visibility=Visibility.PUBLIC,
        )
        db.add(segment)
        db.add(activity)
        db.commit()
        effort = SegmentEffort(
            segment_id=segment.id, activity_id=activity.id, athlete_id=user.id, elapsed_time=120
        )
        db.add(effort)
        db.commit()
        resp = client.get(f"/segments/{segment.id}/efforts", headers=headers)
        assert resp.status_code == 200
