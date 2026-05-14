from backend.models.user import User
from backend.services import auth_service
from backend.tests.conftest import MOCK_HASH


class TestGetMe:
    def test_get_me(self, client, auth_user):
        user, headers = auth_user
        resp = client.get("/users/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/users/me")
        assert resp.status_code in (401, 403, 422)


class TestUpdateMe:
    def test_update_me_bio(self, client, auth_user):
        user, headers = auth_user
        resp = client.patch("/users/me", json={"bio": "Hello world"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["bio"] == "Hello world"

    def test_update_me_username(self, client, auth_user):
        user, headers = auth_user
        resp = client.patch("/users/me", json={"username": "newname"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "newname"

    def test_update_me_duplicate_username(self, client, auth_user, second_user):
        user, headers = auth_user
        resp = client.patch("/users/me", json={"username": second_user.username}, headers=headers)
        assert resp.status_code == 400


class TestGetUser:
    def test_get_user_by_id(self, client, auth_user):
        user, headers = auth_user
        resp = client.get(f"/users/{user.id}", headers=headers)
        assert resp.status_code == 200

    def test_get_user_not_found(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/users/9999", headers=headers)
        assert resp.status_code == 404


class TestFriendRequests:
    def test_send_friend_request(self, client, auth_user, second_user):
        user, headers = auth_user
        resp = client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        assert resp.status_code == 201
        assert resp.json()["status"] == "pending"

    def test_send_friend_request_to_self(self, client, auth_user):
        user, headers = auth_user
        resp = client.post(f"/users/{user.id}/friend-request", headers=headers)
        assert resp.status_code == 400

    def test_send_friend_request_twice(self, client, auth_user, second_user):
        _, headers = auth_user
        client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        resp = client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        assert resp.status_code == 400


class TestAcceptFriendRequest:
    def test_accept_friend_request(self, client, auth_user, second_user_auth):
        user, headers = auth_user
        client.post(f"/users/{second_user_auth[0].id}/friend-request", headers=headers)
        resp = client.post(f"/users/{user.id}/accept-friend", headers=second_user_auth[1])
        assert resp.status_code == 200
        assert resp.json()["status"] == "accepted"

    def test_accept_no_pending_request(self, client, auth_user, second_user):
        _, headers = auth_user
        resp = client.post(f"/users/{second_user.id}/accept-friend", headers=headers)
        assert resp.status_code == 404


class TestRemoveFriend:
    def test_remove_friend_accepted(self, client, db, auth_user, second_user, second_user_auth):
        user, headers = auth_user
        client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        client.post(f"/users/{user.id}/accept-friend", headers=second_user_auth[1])
        resp = client.delete(f"/users/{second_user.id}/friend", headers=headers)
        assert resp.status_code == 204

    def test_remove_friend_not_found(self, client, auth_user, second_user):
        _, headers = auth_user
        resp = client.delete(f"/users/{second_user.id}/friend", headers=headers)
        assert resp.status_code == 404


class TestFriendLists:
    def test_list_friends_from(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        client.post(f"/users/{second_user_auth[0].id}/friend-request", headers=second_user_auth[1])
        client.post(f"/users/{second_user_auth[0].id}/accept-friend", headers=headers)
        resp = client.get("/users/me/friends/incoming", headers=headers)
        assert resp.status_code == 200

    def test_list_friends(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        client.post(f"/users/{second_user_auth[0].id}/friend-request", headers=headers)
        client.post(f"/users/{user.id}/accept-friend", headers=second_user_auth[1])
        resp = client.get("/users/me/friends", headers=headers)
        assert resp.status_code == 200

    def test_list_pending_friend_requests(self, client, auth_user, second_user_auth):
        user, headers = auth_user
        client.post(f"/users/{user.id}/friend-request", headers=second_user_auth[1])
        resp = client.get("/users/me/friend-requests/pending", headers=headers)
        assert resp.status_code == 200


class TestSearchUsers:
    def test_search_excludes_self(self, client, auth_user, second_user):
        user, headers = auth_user
        resp = client.get("/users/search", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert user.id not in [u["id"] for u in results]

    def test_search_excludes_friends_bidirectional(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        second_user, second_headers = second_user_auth
        client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        client.post(f"/users/{user.id}/accept-friend", headers=second_headers)
        resp = client.get("/users/search", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert second_user.id not in [u["id"] for u in results]

    def test_search_excludes_pending_incoming(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        second_user, second_headers = second_user_auth
        client.post(f"/users/{user.id}/friend-request", headers=second_headers)
        resp = client.get("/users/search", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert second_user.id not in [u["id"] for u in results]

    def test_search_excludes_pending_outgoing(self, client, db, auth_user, second_user):
        user, headers = auth_user
        client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        resp = client.get("/users/search", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert second_user.id not in [u["id"] for u in results]

    def test_search_with_query_includes_incoming_request(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        second_user, second_headers = second_user_auth
        client.post(f"/users/{user.id}/friend-request", headers=second_headers)
        resp = client.get("/users/search?q=other", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert second_user.id in [u["id"] for u in results]

    def test_search_with_query_includes_friends(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        second_user, second_headers = second_user_auth
        client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        client.post(f"/users/{user.id}/accept-friend", headers=second_headers)
        resp = client.get("/users/search?q=other", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert second_user.id in [u["id"] for u in results]

    def test_search_with_query_includes_outgoing_request(self, client, db, auth_user, second_user):
        user, headers = auth_user
        client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        resp = client.get("/users/search?q=other", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert second_user.id in [u["id"] for u in results]

    def test_search_returns_unrelated_users(self, client, db, auth_user, second_user):
        user, headers = auth_user
        resp = client.get("/users/search", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert second_user.id in [u["id"] for u in results]

    def test_search_case_insensitive(self, client, db, auth_user, second_user):
        user, headers = auth_user
        resp = client.get("/users/search?q=OTHER", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert second_user.id in [u["id"] for u in results]

    def test_search_returns_only_unrelated_users(self, client, db, auth_user, second_user):
        user, headers = auth_user
        resp = client.get("/users/search", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        result_ids = [u["id"] for u in results]
        assert user.id not in result_ids
        assert second_user.id in result_ids

    def test_search_excludes_current_user_with_query(self, client, auth_user, second_user):
        user, headers = auth_user
        resp = client.get(f"/users/search?q={user.username}", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert user.id not in [u["id"] for u in results]

    def test_search_no_match_returns_empty(self, client, db, auth_user, second_user):
        user, headers = auth_user
        resp = client.get("/users/search?q=nonexistentuser", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 0


class TestIncomingFriendRequests:
    def test_empty_when_no_requests(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/users/me/friend-requests/incoming", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_incoming_request(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        second_user, second_headers = second_user_auth
        client.post(f"/users/{user.id}/friend-request", headers=second_headers)
        resp = client.get("/users/me/friend-requests/incoming", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1
        assert results[0]["requester_id"] == second_user.id
        assert results[0]["requester"]["id"] == second_user.id
        assert results[0]["status"] == "pending"

    def test_excludes_accepted_friendships(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        second_user, second_headers = second_user_auth
        client.post(f"/users/{user.id}/friend-request", headers=second_headers)
        client.post(f"/users/{second_user.id}/accept-friend", headers=headers)
        resp = client.get("/users/me/friend-requests/incoming", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_multiple_incoming_requests(self, client, db, auth_user, second_user, second_user_auth):
        user, headers = auth_user
        _, second_headers = second_user_auth
        third_user = User(username="thirduser", email="third@test.com", password_hash=MOCK_HASH)
        db.add(third_user)
        db.commit()
        db.refresh(third_user)
        client.post(f"/users/{user.id}/friend-request", headers=second_headers)
        token3 = auth_service.create_access_token(third_user.id)
        client.post(f"/users/{user.id}/friend-request", headers={"Authorization": f"Bearer {token3}"})
        resp = client.get("/users/me/friend-requests/incoming", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 2
        requester_ids = [r["requester_id"] for r in results]
        assert second_user.id in requester_ids
        assert third_user.id in requester_ids


class TestSentFriendRequests:
    def test_empty_when_no_requests(self, client, auth_user):
        _, headers = auth_user
        resp = client.get("/users/me/friend-requests/sent", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_sent_request(self, client, db, auth_user, second_user):
        user, headers = auth_user
        client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        resp = client.get("/users/me/friend-requests/sent", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1
        assert results[0]["addressee_id"] == second_user.id
        assert results[0]["addressee"]["id"] == second_user.id
        assert results[0]["status"] == "pending"

    def test_excludes_accepted_friendships(self, client, db, auth_user, second_user_auth):
        user, headers = auth_user
        second_user, second_headers = second_user_auth
        client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        client.post(f"/users/{user.id}/accept-friend", headers=second_headers)
        resp = client.get("/users/me/friend-requests/sent", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_multiple_sent_requests(self, client, db, auth_user, second_user):
        user, headers = auth_user
        third_user = User(username="thirduser2", email="third2@test.com", password_hash=MOCK_HASH)
        db.add(third_user)
        db.commit()
        db.refresh(third_user)
        client.post(f"/users/{second_user.id}/friend-request", headers=headers)
        client.post(f"/users/{third_user.id}/friend-request", headers=headers)
        resp = client.get("/users/me/friend-requests/sent", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 2
        addressee_ids = [r["addressee_id"] for r in results]
        assert second_user.id in addressee_ids
        assert third_user.id in addressee_ids

    def test_only_own_requests(self, client, db, auth_user, second_user, second_user_auth):
        _, headers = auth_user
        second_user, second_headers = second_user_auth
        third_user = User(username="fourthuser", email="fourth@test.com", password_hash=MOCK_HASH)
        db.add(third_user)
        db.commit()
        db.refresh(third_user)
        client.post(f"/users/{third_user.id}/friend-request", headers=second_headers)
        resp = client.get("/users/me/friend-requests/sent", headers=headers)
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 0
