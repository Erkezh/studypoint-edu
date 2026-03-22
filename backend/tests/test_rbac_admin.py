from __future__ import annotations


async def test_student_cannot_access_admin_endpoints(client, student_token):
    resp = await client.get("/api/v1/admin/subjects", headers={"Authorization": f"Bearer {student_token}"})
    assert resp.status_code == 403, resp.text


async def test_admin_can_access_admin_endpoints(client, admin_token):
    resp = await client.get("/api/v1/admin/subjects", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json()["data"], list)


async def test_admin_can_create_grade_without_description(client, admin_token):
    resp = await client.post(
        "/api/v1/admin/grades",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"number": 97, "label": "T97", "title": "Temp Grade 97"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["description"] == ""
