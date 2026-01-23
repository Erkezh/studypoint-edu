from __future__ import annotations

import uuid


async def test_auth_register_login_refresh_logout(client):
    email = f"user-{uuid.uuid4()}@example.com"
    password = "Password123!"

    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User", "role": "STUDENT", "grade_level": 5},
    )
    assert r.status_code == 200, r.text
    tokens = r.json()["data"]
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200, me.text
    assert me.json()["data"]["email"] == email

    refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200, refreshed.text
    new_tokens = refreshed.json()["data"]
    assert new_tokens["access_token"]
    assert new_tokens["refresh_token"]

    logout = await client.post("/api/v1/auth/logout", json={"refresh_token": new_tokens["refresh_token"]})
    assert logout.status_code == 200, logout.text

    # token should now be revoked
    refresh_again = await client.post("/api/v1/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]})
    assert refresh_again.status_code == 401

