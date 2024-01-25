from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app import models
from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token


# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:password123@localhost:5432/fastapi_test'
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "test@test.com", "password": "password"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_second_user(client):
    user_data = {"email": "seconduser@test.com", "password": "password"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    return client


@pytest.fixture
def test_posts(test_user, test_second_user, session):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "owner_id": test_user["id"],
        },
        {
            "title": "second title",
            "content": "second content",
            "owner_id": test_user["id"],
        },
        {
            "title": "first title",
            "content": "third content",
            "owner_id": test_user["id"],
        },
        {
            "title": "first title second user",
            "content": "third content second user",
            "owner_id": test_second_user["id"],
        },
    ]

    posts_map = map(lambda post: models.Post(**post), posts_data)
    posts = list(posts_map)

    session.add_all(posts)
    session.commit()

    fetched_posts = session.query(models.Post).all()
    return fetched_posts
