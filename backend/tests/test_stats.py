from backend.models.activity import Activity, SportType


class TestStats:
    def test_stats_totals(self, client, db, auth_user):
        user, headers = auth_user
        db.add(Activity(owner_id=user.id, title="Run 1", sport_type=SportType.RUN, distance=5000, duration=1800, elevation=50))
        db.commit()
        resp = client.get("/stats/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "totals" in data
        assert "personal_records" in data

    def test_stats_filter_by_sport(self, client, db, auth_user):
        user, headers = auth_user
        db.add(Activity(owner_id=user.id, title="Run 1", sport_type=SportType.RUN, distance=5000))
        db.add(Activity(owner_id=user.id, title="Ride 1", sport_type=SportType.RIDE, distance=20000))
        db.commit()
        resp = client.get("/stats/me?sport_type=run", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "run" in data["totals"]
        assert "ride" not in data["totals"]

    def test_stats_empty(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/stats/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["totals"] == {}
        assert data["personal_records"] == []