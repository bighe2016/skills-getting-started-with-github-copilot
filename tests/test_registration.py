import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.fixture
def activity(monkeypatch):
    name = "Test Activity"
    monkeypatch.setitem(
        app_module.activities,
        name,
        {
            "description": "Activity used in registration tests",
            "schedule": "Mondays",
            "max_participants": 2,
            "participants": [],
        },
    )
    return name


def test_signup_adds_student_to_activity(client, activity):
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up student@example.com for {activity}"
    }
    assert app_module.activities[activity]["participants"] == ["student@example.com"]


def test_duplicate_signup_is_rejected_without_adding_another_entry(client, activity):
    app_module.activities[activity]["participants"].append("student@example.com")

    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert app_module.activities[activity]["participants"] == ["student@example.com"]


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_student_from_activity(client, activity):
    app_module.activities[activity]["participants"].append("student@example.com")

    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered student@example.com from {activity}"
    }
    assert app_module.activities[activity]["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unregistered_student(client, activity):
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert app_module.activities[activity]["participants"] == []
