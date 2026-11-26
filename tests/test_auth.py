import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def new_user():
    # A different email each time, so tests never clash with each other.
    return {
        "full_name": "Test User",
        "email": f"test_{uuid.uuid4().hex}@example.com",
        "password": "Secret12345",
    }


def test_register_creates_a_user():
    user = new_user()

    response = client.post("/auth/register", json=user)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == user["email"]
    assert body["role"] == "user"
    # The password must never be sent back.
    assert "password" not in body
    assert "password_hash" not in body


def test_register_same_email_twice_is_rejected():
    user = new_user()

    first = client.post("/auth/register", json=user)
    second = client.post("/auth/register", json=user)

    assert first.status_code == 201
    assert second.status_code == 409


def test_login_gives_tokens():
    user = new_user()
    client.post("/auth/register", json=user)

    response = client.post(
        "/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


def test_login_with_wrong_password_is_rejected():
    user = new_user()
    client.post("/auth/register", json=user)

    response = client.post(
        "/auth/login",
        json={"email": user["email"], "password": "WrongPassword999"},
    )

    assert response.status_code == 401
