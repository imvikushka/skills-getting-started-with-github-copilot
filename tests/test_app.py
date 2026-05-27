import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)
_original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity_success():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]

    activities_data = client.get("/activities").json()
    assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_unregister_participant_success():
    client.post(
        "/activities/Soccer Team/signup",
        params={"email": "testremove@mergington.edu"},
    )

    response = client.delete(
        "/activities/Soccer Team/participants/testremove@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]

    activities_data = client.get("/activities").json()
    assert "testremove@mergington.edu" not in activities_data["Soccer Team"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        "/activities/Basketball Club/participants/nonexistent@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]
