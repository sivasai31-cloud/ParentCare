def register_user(client, email):
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_readings_are_validated_and_private(client):
    owner_headers = register_user(client, "health-owner@example.com")
    other_headers = register_user(client, "health-other@example.com")

    parent_response = client.post(
        "/api/parents",
        json={"name": "Care Recipient"},
        headers=owner_headers,
    )
    assert parent_response.status_code == 201
    parent_id = parent_response.json()["id"]

    invalid_response = client.post(
        "/api/health-readings",
        json={
            "parent_id": parent_id,
            "metric": "blood_pressure",
            "value": 120,
            "unit": "mmHg",
        },
        headers=owner_headers,
    )
    assert invalid_response.status_code == 422

    create_response = client.post(
        "/api/health-readings",
        json={
            "parent_id": parent_id,
            "metric": "blood_pressure",
            "value": 120,
            "secondary_value": 80,
            "unit": "mmHg",
            "recorded_at": "2026-11-21T10:00:00Z",
        },
        headers=owner_headers,
    )
    assert create_response.status_code == 201
    reading_id = create_response.json()["id"]
    assert create_response.json()["value"] == 120
    assert create_response.json()["secondary_value"] == 80

    hidden_readings = client.get(
        f"/api/health-readings?parent_id={parent_id}",
        headers=other_headers,
    )
    assert hidden_readings.status_code == 200
    assert hidden_readings.json() == []

    denied_delete = client.delete(
        f"/api/health-readings/{reading_id}",
        headers=other_headers,
    )
    assert denied_delete.status_code == 403

    deleted = client.delete(
        f"/api/health-readings/{reading_id}",
        headers=owner_headers,
    )
    assert deleted.status_code == 204
