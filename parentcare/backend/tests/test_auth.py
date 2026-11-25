def test_register_and_login(client):
    # Test Registration
    reg_payload = {
        "email": "child@example.com",
        "password": "Password123!",
        "full_name": "Alex Smith",
        "phone": "+1 555-0199",
        "role": "USER"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "child@example.com"
    assert data["user"]["role"] == "USER"

    # Test Duplicate Registration Prevention
    res_dup = client.post("/api/auth/register", json=reg_payload)
    assert res_dup.status_code == 400

    # Test Login
    login_payload = {
        "email": "child@example.com",
        "password": "Password123!"
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]

    # Test Get Current User (/api/auth/me)
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["full_name"] == "Alex Smith"


def test_public_registration_cannot_grant_admin_role(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "self-appointed-admin@example.com",
            "password": "Password123!",
            "full_name": "Unprivileged User",
            "role": "ADMIN",
        },
    )

    assert response.status_code == 201
    assert response.json()["user"]["role"] == "USER"

    token = response.json()["access_token"]
    stats_response = client.get(
        "/api/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert stats_response.status_code == 403


def test_forgot_password_does_not_expose_reset_token_in_production(client, monkeypatch):
    from app.core.config import settings

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "reset-user@example.com",
            "password": "Password123!",
            "full_name": "Reset User",
        },
    )
    assert register_response.status_code == 201
    monkeypatch.setattr(settings, "APP_ENV", "production")

    response = client.post(
        "/api/auth/forgot-password",
        json={"email": "reset-user@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["reset_token"] == ""
    assert "If that email is registered" in response.json()["message"]
