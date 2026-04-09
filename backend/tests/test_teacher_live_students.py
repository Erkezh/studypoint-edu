from __future__ import annotations

import uuid

import pytest
from redis.asyncio import Redis
from sqlalchemy import update
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.security import hash_password
from app.models.profile import StudentProfile
from app.models.user import User


async def _login(client, email: str, password: str) -> dict:
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["data"]


async def _clear_presence() -> None:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        async for key in redis.scan_iter(match="student:presence:*"):
            await redis.delete(key)
    finally:
        await redis.aclose()


async def _restore_seeded_student_password() -> None:
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(
                update(User)
                .where(User.email == "student@example.com")
                .values(password_hash=hash_password("Password123!"))
            )
            await conn.execute(
                update(StudentProfile)
                .where(StudentProfile.user_id == User.id)
                .where(User.email == "student@example.com")
                .values(plain_password=None)
            )
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_live_students_includes_enrolled_only_student(client, cleanup_practice_tables):
    await _clear_presence()

    teacher = await _login(client, "teacher@example.com", "Password123!")
    student = await _login(client, "student@example.com", "Password123!")

    start = await client.post(
        "/api/v1/practice/sessions",
        json={"skill_id": 1},
        headers={"Authorization": f"Bearer {student['access_token']}", "Idempotency-Key": "live-scope-seeded-start"},
    )
    assert start.status_code == 200, start.text

    live = await client.get(
        "/api/v1/teacher/live-students",
        headers={"Authorization": f"Bearer {teacher['access_token']}"},
    )
    assert live.status_code == 200, live.text

    payload = live.json()["data"]
    assert payload["total_students"] == 1
    assert payload["active_count"] == 1
    assert payload["inactive_count"] == 0
    assert payload["inactive_students"] == []
    assert [entry["student_id"] for entry in payload["students"]] == [student["user"]["id"]]
    assert payload["students"][0]["full_name"] == "Student"


@pytest.mark.asyncio
async def test_live_students_deduplicates_direct_and_enrolled_student(client, cleanup_practice_tables):
    await _clear_presence()

    teacher = await _login(client, "teacher@example.com", "Password123!")
    seeded_student = await _login(client, "student@example.com", "Password123!")
    teacher_token = teacher["access_token"]
    created_student_id: str | None = None

    try:
        created = await client.post(
            "/api/v1/teacher/students",
            json={"first_name": "Direct", "last_name": "Student", "grade_id": 7},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert created.status_code == 200, created.text
        created_student = created.json()["data"]
        created_student_id = created_student["id"]

        classroom = await client.post(
            "/api/v1/classrooms",
            json={"title": f"Live Scope {uuid.uuid4().hex[:6]}", "grade_id": 7},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert classroom.status_code == 200, classroom.text
        classroom_id = classroom.json()["data"]["id"]

        enroll = await client.post(
            f"/api/v1/classrooms/{classroom_id}/enroll",
            json={"student_id": created_student_id},
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert enroll.status_code == 200, enroll.text

        created_login = await _login(client, created_student["username"], created_student["password"])
        start = await client.post(
            "/api/v1/practice/sessions",
            json={"skill_id": 1},
            headers={"Authorization": f"Bearer {created_login['access_token']}", "Idempotency-Key": "live-scope-direct-enrolled-start"},
        )
        assert start.status_code == 200, start.text

        live = await client.get(
            "/api/v1/teacher/live-students",
            headers={"Authorization": f"Bearer {teacher_token}"},
        )
        assert live.status_code == 200, live.text

        payload = live.json()["data"]
        active_ids = [entry["student_id"] for entry in payload["students"]]
        assert payload["total_students"] == 2
        assert payload["active_count"] == 1
        assert payload["inactive_count"] == 1
        assert active_ids.count(created_student_id) == 1
        assert payload["inactive_students"] == [
            {
                "student_id": seeded_student["user"]["id"],
                "full_name": "Student",
            }
        ]
    finally:
        if created_student_id is not None:
            delete_student = await client.delete(
                f"/api/v1/teacher/students/{created_student_id}",
                headers={"Authorization": f"Bearer {teacher_token}"},
            )
            assert delete_student.status_code == 200, delete_student.text


@pytest.mark.asyncio
async def test_live_students_reports_inactive_scoped_students_consistently(client, cleanup_practice_tables):
    await _clear_presence()

    teacher = await _login(client, "teacher@example.com", "Password123!")
    student = await _login(client, "student@example.com", "Password123!")

    live = await client.get(
        "/api/v1/teacher/live-students",
        headers={"Authorization": f"Bearer {teacher['access_token']}"},
    )
    assert live.status_code == 200, live.text

    payload = live.json()["data"]
    assert payload["total_students"] == 1
    assert payload["active_count"] == 0
    assert payload["inactive_count"] == 1
    assert payload["students"] == []
    assert payload["inactive_students"] == [
        {
            "student_id": student["user"]["id"],
            "full_name": "Student",
        }
    ]


@pytest.mark.asyncio
async def test_teacher_student_analytics_allows_enrolled_only_student(client, cleanup_practice_tables):
    teacher = await _login(client, "teacher@example.com", "Password123!")
    student = await _login(client, "student@example.com", "Password123!")

    response = await client.get(
        f"/api/v1/teacher/students/{student['user']['id']}/analytics",
        headers={"Authorization": f"Bearer {teacher['access_token']}"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()["data"]
    assert set(payload.keys()) == {"overview", "skills", "all_questions"}


@pytest.mark.asyncio
async def test_teacher_can_reset_password_for_enrolled_only_student(client, cleanup_practice_tables):
    teacher = await _login(client, "teacher@example.com", "Password123!")
    student = await _login(client, "student@example.com", "Password123!")

    try:
        response = await client.post(
            f"/api/v1/teacher/students/{student['user']['id']}/reset-password",
            headers={"Authorization": f"Bearer {teacher['access_token']}"},
        )
        assert response.status_code == 200, response.text
        payload = response.json()["data"]
        assert payload["username"] == "student@example.com"
        assert isinstance(payload["password"], str)
        assert payload["password"]
    finally:
        await _restore_seeded_student_password()


@pytest.mark.asyncio
async def test_teacher_can_delete_enrolled_only_student(client, cleanup_practice_tables):
    teacher = await _login(client, "teacher@example.com", "Password123!")
    teacher_token = teacher["access_token"]

    email = f"delete-{uuid.uuid4().hex[:8]}@example.com"
    registered = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Delete Me",
            "role": "STUDENT",
            "grade_level": 5,
        },
    )
    assert registered.status_code == 200, registered.text
    student_id = registered.json()["data"]["user"]["id"]

    classroom = await client.post(
        "/api/v1/classrooms",
        json={"title": f"Delete Scope {uuid.uuid4().hex[:6]}", "grade_id": 7},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert classroom.status_code == 200, classroom.text
    classroom_id = classroom.json()["data"]["id"]

    enroll = await client.post(
        f"/api/v1/classrooms/{classroom_id}/enroll",
        json={"student_id": student_id},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert enroll.status_code == 200, enroll.text

    delete_response = await client.delete(
        f"/api/v1/teacher/students/{student_id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["data"] == {"deleted": student_id}
