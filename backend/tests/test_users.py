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
