import copy

from fastapi.testclient import TestClient
from src import app as app_module


# Keep an original copy of in-memory data so tests start cleanly
ORIG_ACTIVITIES = copy.deepcopy(app_module.activities)


import pytest


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(ORIG_ACTIVITIES)
    yield


client = TestClient(app_module.app)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success():
    r = client.post("/activities/Chess%20Club/signup?email=new@mergington.edu")
    assert r.status_code == 200
    assert "Signed up new@mergington.edu for Chess Club" in r.json().get("message", "")
    r2 = client.get("/activities")
    assert "new@mergington.edu" in r2.json()["Chess Club"]["participants"]


def test_duplicate_signup():
    r1 = client.post("/activities/Chess%20Club/signup?email=dup@mergington.edu")
    assert r1.status_code == 200
    r2 = client.post("/activities/Chess%20Club/signup?email=dup@mergington.edu")
    assert r2.status_code == 400


def test_unregister_success():
    # michael@mergington.edu is present in initial fixtures
    r = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")
    assert r.status_code == 200
    r2 = client.get("/activities")
    assert "michael@mergington.edu" not in r2.json()["Chess Club"]["participants"]


def test_unregister_nonexistent():
    r = client.delete("/activities/Chess%20Club/participants?email=nope@mergington.edu")
    assert r.status_code == 404


def test_activity_not_found_signup_and_unregister():
    r1 = client.post("/activities/Unknown%20Activity/signup?email=a@b.com")
    assert r1.status_code == 404
    r2 = client.delete("/activities/Unknown%20Activity/participants?email=a@b.com")
    assert r2.status_code == 404
