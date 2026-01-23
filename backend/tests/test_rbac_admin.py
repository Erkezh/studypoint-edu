from __future__ import annotations


async def test_student_cannot_access_admin_endpoints(client, student_token):
    resp = await client.get("/api/v1/admin/subjects", headers={"Authorization": f"Bearer {student_token}"})
    assert resp.status_code == 403, resp.text


async def test_admin_can_access_admin_endpoints(client, admin_token):
    resp = await client.get("/api/v1/admin/subjects", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json()["data"], list)

