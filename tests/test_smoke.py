from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_page_says_running():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Booking System API is running"}


def test_docs_schema_can_be_built():
    # This fails if any route or schema cannot be built,
    # for example when a library such as email-validator is missing.
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["paths"]
