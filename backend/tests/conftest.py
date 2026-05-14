import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from backend.database import get_db
from backend.main import app
from backend.models.user import User
from backend.services import auth_service

MOCK_HASH = "$2b$12$fakehashfakehashfakehashfakehashfake"

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://runbandits:runbandits@localhost:5432/runbandits",
)

engine = create_engine(DATABASE_URL)


@pytest.fixture(autouse=True)
def mock_hash_password():
    with patch.object(auth_service, "hash_password", return_value=MOCK_HASH):
        with patch.object(auth_service, "verify_password", return_value=True):
            yield


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session_local = sessionmaker(bind=connection)
    session = session_local()

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_user(db):
    user = User(username="testuser", email="test@example.com", password_hash=MOCK_HASH)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = auth_service.create_access_token(user.id)
    return user, {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user(db):
    user = User(username="otheruser", email="other@example.com", password_hash=MOCK_HASH)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def second_user_auth(db, second_user):
    token = auth_service.create_access_token(second_user.id)
    return second_user, {"Authorization": f"Bearer {token}"}
