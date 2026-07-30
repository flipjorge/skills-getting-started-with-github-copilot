from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_unregister_participant():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = activities[activity_name]["participants"][:]

    try:
        response = client.post(f"/activities/{activity_name}/unregister?email={email}")

        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
    finally:
        activities[activity_name]["participants"] = original_participants


def test_activities_response_is_not_cached():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "no-store" in response.headers.get("cache-control", "")
