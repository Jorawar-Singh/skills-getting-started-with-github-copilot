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
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_data(client, activities):
    # Arrange
    expected_activities = activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activities):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post(
        "/activities/Robotics Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Robotics Club"}
    assert email in activities["Robotics Club"]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "new@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_for_duplicate_participant(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.post(
        "/activities/Robotics Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_unregister_removes_participant(client, activities):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete(
        "/activities/Robotics Club/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Robotics Club"}
    assert email not in activities["Robotics Club"]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "existing@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_404_for_unregistered_participant(client):
    # Arrange
    email = "missing@example.com"

    # Act
    response = client.delete(
        "/activities/Robotics Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }