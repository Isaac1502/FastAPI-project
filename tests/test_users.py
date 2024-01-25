import pytest

from app import schemas
from .database import client, session


def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "test@test.com", "password": "password"}
    )
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "test@test.com"
    assert res.status_code == 201


def test_login_user(client):
    res = client.post(
        "/login", data={"username": "test@test.com", "password": "password"}
    )
    assert res.status_code == 200
