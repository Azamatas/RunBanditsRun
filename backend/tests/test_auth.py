class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_register_duplicate_email(self, client, auth_user):
        user, _ = auth_user
        resp = client.post("/auth/register", json={
            "username": "another",
            "email": user.email,
            "password": "password123",
        })
        assert resp.status_code == 400
        assert "Email already registered" in resp.json()["detail"]

    def test_register_duplicate_username(self, client, auth_user):
        user, _ = auth_user
        resp = client.post("/auth/register", json={
            "username": user.username,
            "email": "unique@example.com",
            "password": "password123",
        })
        assert resp.status_code == 400
        assert "Username already taken" in resp.json()["detail"]

    def test_register_short_password(self, client):
        resp = client.post("/auth/register", json={
            "username": "shortpw",
            "email": "short@example.com",
            "password": "short",
        })
        assert resp.status_code == 422

    def test_register_short_username(self, client):
        resp = client.post("/auth/register", json={
            "username": "ab",
            "email": "shortuser@example.com",
            "password": "password123",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client, auth_user):
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_nonexistent_email(self, client, auth_user):
        resp = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401


class TestRefreshToken:
    def test_refresh_success(self, client, auth_user):
        _, headers = auth_user
        login_resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })
        refresh_token = login_resp.json()["refresh_token"]
        resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    def test_refresh_with_access_token(self, client, auth_user):
        _, headers = auth_user
        access_token = headers["Authorization"].replace("Bearer ", "")
        resp = client.post("/auth/refresh", json={"refresh_token": access_token})
        assert resp.status_code == 401

    def test_refresh_invalid_token(self, client):
        resp = client.post("/auth/refresh", json={"refresh_token": "invalidtoken"})
        assert resp.status_code == 401