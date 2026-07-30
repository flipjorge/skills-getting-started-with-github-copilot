import asyncio
import copy

import pytest
from httpx import ASGITransport, AsyncClient

import src.app as app_module
from src.app import app


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_state))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_state))


def make_async_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


def make_request(method: str, path: str, **kwargs):
    async def _request():
        async with make_async_client() as client:
            return await getattr(client, method.lower())(path, **kwargs)

    return asyncio.run(_request())


def test_get_activities_returns_known_activities():
    response = make_request("get", "/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12


def test_signup_adds_participant_to_activity():
    email = "newstudent@example.com"

    response = make_request("post", "/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "duplicate@example.com"
    make_request("post", "/activities/Chess Club/signup", params={"email": email})

    response = make_request("post", "/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant_from_activity():
    email = "leavingstudent@example.com"
    make_request("post", "/activities/Chess Club/signup", params={"email": email})

    response = make_request("post", "/activities/Chess Club/unregister", params={"email": email})

    assert response.status_code == 200
    assert email not in app_module.activities["Chess Club"]["participants"]
