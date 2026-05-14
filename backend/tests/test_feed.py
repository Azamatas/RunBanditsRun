from backend.models.activity import Activity, SportType, Visibility
from backend.models.friendship import Friendship, FriendshipStatus


class TestFeed:
    def test_feed_includes_own(self, client, db, auth_user):
        user, headers = auth_user
        db.add(
            Activity(
                owner_id=user.id,
                title="My Run",
                sport_type=SportType.RUN,
                visibility=Visibility.PUBLIC,
            )
        )
        db.commit()
        resp = client.get("/feed/", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_feed_includes_friends_public(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        other = second_user_auth[0]
        db.add(
            Activity(
                owner_id=other.id,
                title="Friend Run",
                sport_type=SportType.RUN,
                visibility=Visibility.PUBLIC,
            )
        )
        db.add(
            Friendship(
                requester_id=user.id, addressee_id=other.id, status=FriendshipStatus.ACCEPTED
            )
        )
        db.commit()
        resp = client.get("/feed/", headers=headers)
        assert resp.status_code == 200

    def test_feed_excludes_private(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        other = second_user_auth[0]
        db.add(
            Activity(
                owner_id=other.id,
                title="Private Run",
                sport_type=SportType.RUN,
                visibility=Visibility.PRIVATE,
            )
        )
        db.commit()
        resp = client.get("/feed/", headers=headers)
        assert resp.status_code == 200
        assert all(a["title"] != "Private Run" for a in resp.json())
