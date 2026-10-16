import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities():
    return {
        "Robotics Club": {
            "description": "Build and program robots",
            "schedule": "Fridays, 3:00 PM",
            "max_participants": 10,
            "participants": ["existing@example.com"],
        }
    }


@pytest.fixture
def client(monkeypatch, activities):
    monkeypatch.setattr(app_module, "activities", activities)
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_root_redirects_to_frontend(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client, activities):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client, activities):
    email = "new@example.com"

    response = client.post(
        "/activities/Robotics Club/signup", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Robotics Club"}
    assert email in activities["Robotics Club"]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup", params={"email": "new@example.com"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_for_duplicate_participant(client):
    response = client.post(
        "/activities/Robotics Club/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_unregister_removes_participant(client, activities):
    email = "existing@example.com"

    response = client.delete(
        "/activities/Robotics Club/participants", params={"email": email}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Robotics Club"}
    assert email not in activities["Robotics Club"]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_404_for_unregistered_participant(client):
    response = client.delete(
        "/activities/Robotics Club/participants",
        params={"email": "missing@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }