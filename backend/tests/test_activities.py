from backend.models.activity import Activity, SportType, Visibility
from backend.models.friendship import Friendship, FriendshipStatus


class TestCreateActivity:
    def test_create_activity(self, client, auth_user):
        _, headers = auth_user
        resp = client.post(
            "/activities/",
            json={
                "title": "Morning Run",
                "sport_type": "run",
                "distance": 5000,
                "duration": 1800,
                "visibility": "public",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Morning Run"
        assert data["kudos_count"] == 0

    def test_create_activity_with_tagged(self, client, auth_user, second_user):
        user, headers = auth_user
        resp = client.post(
            "/activities/",
            json={
                "title": "Group Ride",
                "sport_type": "ride",
                "tagged_athlete_ids": [second_user.id],
            },
            headers=headers,
        )
        assert resp.status_code == 200


class TestGetActivity:
    def test_get_activity_public(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        activity = Activity(
            owner_id=user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.PUBLIC
        )
        db.add(activity)
        db.commit()
        resp = client.get(f"/activities/{activity.id}", headers=second_user_auth[1])
        assert resp.status_code == 200

    def test_get_activity_friends_only(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        activity = Activity(
            owner_id=user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.FRIENDS
        )
        db.add(activity)
        db.commit()
        resp = client.get(f"/activities/{activity.id}", headers=second_user_auth[1])
        assert resp.status_code == 404

    def test_get_activity_friends_visible_to_friend(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        activity = Activity(
            owner_id=user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.FRIENDS
        )
        db.add(activity)
        db.add(
            Friendship(
                requester_id=user.id,
                addressee_id=second_user_auth[0].id,
                status=FriendshipStatus.ACCEPTED,
            )
        )
        db.commit()
        resp = client.get(f"/activities/{activity.id}", headers=second_user_auth[1])
        assert resp.status_code == 200

    def test_get_activity_private(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        activity = Activity(
            owner_id=user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.PRIVATE
        )
        db.add(activity)
        db.commit()
        resp = client.get(f"/activities/{activity.id}", headers=second_user_auth[1])
        assert resp.status_code == 404

    def test_get_own_private_activity(self, client, db, auth_user):
        user, headers = auth_user
        activity = Activity(
            owner_id=user.id, title="Run", sport_type=SportType.RUN, visibility=Visibility.PRIVATE
        )
        db.add(activity)
        db.commit()
        resp = client.get(f"/activities/{activity.id}", headers=headers)
        assert resp.status_code == 200


class TestUpdateActivity:
    def test_update_activity(self, client, db, auth_user):
        user, headers = auth_user
        activity = Activity(owner_id=user.id, title="Run", sport_type=SportType.RUN, distance=5000)
        db.add(activity)
        db.commit()
        resp = client.patch(
            f"/activities/{activity.id}",
            json={"title": "Updated Run", "distance": 6000},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Run"
        assert resp.json()["distance"] == 6000

    def test_update_activity_not_owner(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        activity = Activity(owner_id=user.id, title="Run", sport_type=SportType.RUN)
        db.add(activity)
        db.commit()
        resp = client.patch(
            f"/activities/{activity.id}", json={"title": "Hacked"}, headers=second_user_auth[1]
        )
        assert resp.status_code == 404


class TestDeleteActivity:
    def test_delete_activity(self, client, db, auth_user):
        user, headers = auth_user
        activity = Activity(owner_id=user.id, title="Run", sport_type=SportType.RUN)
        db.add(activity)
        db.commit()
        resp = client.delete(f"/activities/{activity.id}", headers=headers)
        assert resp.status_code == 204

    def test_delete_activity_not_owner(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        activity = Activity(owner_id=user.id, title="Run", sport_type=SportType.RUN)
        db.add(activity)
        db.commit()
        resp = client.delete(f"/activities/{activity.id}", headers=second_user_auth[1])
        assert resp.status_code == 404


class TestListActivities:
    def test_list_activities(self, client, db, auth_user):
        user, headers = auth_user
        db.add(
            Activity(
                owner_id=user.id,
                title="Run 1",
                sport_type=SportType.RUN,
                visibility=Visibility.PUBLIC,
            )
        )
        db.add(
            Activity(
                owner_id=user.id,
                title="Ride 1",
                sport_type=SportType.RIDE,
                visibility=Visibility.PUBLIC,
            )
        )
        db.commit()
        resp = client.get("/activities/", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_activities_filter_sport(self, client, db, auth_user):
        user, headers = auth_user
        db.add(
            Activity(
                owner_id=user.id,
                title="Run 1",
                sport_type=SportType.RUN,
                visibility=Visibility.PUBLIC,
            )
        )
        db.add(
            Activity(
                owner_id=user.id,
                title="Ride 1",
                sport_type=SportType.RIDE,
                visibility=Visibility.PUBLIC,
            )
        )
        db.commit()
        resp = client.get("/activities/?sport_type=run", headers=headers)
        assert resp.status_code == 200
        assert all(a["sport_type"] == "run" for a in resp.json())


class TestUserActivities:
    def test_list_user_activities(self, client, db, auth_user):
        user, headers = auth_user
        db.add(
            Activity(
                owner_id=user.id,
                title="Run 1",
                sport_type=SportType.RUN,
                visibility=Visibility.PUBLIC,
            )
        )
        db.commit()
        resp = client.get(f"/users/{user.id}/activities", headers=headers)
        assert resp.status_code == 200
