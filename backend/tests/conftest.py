import pytest
from unittest.mock import patch
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.database import Base, get_db
from backend.main import app
from backend.services import auth_service
from backend.models.user import User


MOCK_HASH = "$2b$12$fakehashfakehashfakehashfakehashfake"

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def mock_hash_password():
    with patch.object(auth_service, "hash_password", return_value=MOCK_HASH):
        with patch.object(auth_service, "verify_password", return_value=True):
            yield


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

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