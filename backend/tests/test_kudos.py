from backend.models.activity import Activity, SportType, Visibility
from backend.models.kudos import Kudos


class TestGiveKudos:
    def test_give_kudos(self, client, db, auth_user, second_user):
        user, headers = auth_user
        activity = Activity(owner_id=second_user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.PUBLIC)
        db.add(activity)
        db.commit()
        resp = client.post(f"/activities/{activity.id}/kudos", headers=headers)
        assert resp.status_code == 201

    def test_give_kudos_count_correct(self, client, db, auth_user, second_user):
        user, headers = auth_user
        activity = Activity(owner_id=second_user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.PUBLIC)
        db.add(activity)
        db.commit()
        resp = client.post(f"/activities/{activity.id}/kudos", headers=headers)
        assert resp.json()["kudos_count"] == 1

    def test_give_kudos_duplicate(self, client, db, auth_user, second_user):
        user, headers = auth_user
        activity = Activity(owner_id=second_user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.PUBLIC)
        db.add(activity)
        db.commit()
        client.post(f"/activities/{activity.id}/kudos", headers=headers)
        resp = client.post(f"/activities/{activity.id}/kudos", headers=headers)
        assert resp.status_code == 400


class TestRemoveKudos:
    def test_remove_kudos(self, client, db, auth_user, second_user):
        user, headers = auth_user
        activity = Activity(owner_id=second_user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.PUBLIC)
        db.add(activity)
        db.commit()
        db.add(Kudos(activity_id=activity.id, user_id=user.id))
        db.commit()
        resp = client.delete(f"/activities/{activity.id}/kudos", headers=headers)
        assert resp.status_code == 204

    def test_remove_kudos_not_found(self, client, db, auth_user, second_user):
        user, headers = auth_user
        activity = Activity(owner_id=second_user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.PUBLIC)
        db.add(activity)
        db.commit()
        resp = client.delete(f"/activities/{activity.id}/kudos", headers=headers)
        assert resp.status_code == 404