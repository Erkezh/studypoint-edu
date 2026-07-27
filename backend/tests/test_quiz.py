from __future__ import annotations

import pytest


async def _login(client, email: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_teacher_quiz_crud_and_student_visibility(client):
    teacher_token = await _login(client, "teacher@example.com")
    student_token = await _login(client, "student@example.com")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    student_headers = {"Authorization": f"Bearer {student_token}"}

    create_response = await client.post(
        "/api/v1/teacher/quizzes",
        headers=teacher_headers,
        json={
            "name": "Quiz integration check",
            "question_order": "FIXED",
            "result_visibility": "ALWAYS",
            "end_type": "MANUAL",
            "questions": [{"question_id": 1, "position": 0}],
        },
    )
    assert create_response.status_code == 200, create_response.text
    created = create_response.json()["data"]
    assert created["name"] == "Quiz integration check"
    assert created["questions"][0]["question_id"] == 1

    teacher_list = await client.get(
        "/api/v1/teacher/quizzes",
        headers=teacher_headers,
    )
    assert teacher_list.status_code == 200, teacher_list.text
    assert any(item["id"] == created["id"] for item in teacher_list.json()["data"])

    student_list = await client.get(
        "/api/v1/student/quizzes/all",
        headers=student_headers,
    )
    assert student_list.status_code == 200, student_list.text
    assert any(item["id"] == created["id"] for item in student_list.json()["data"])

    forbidden = await client.get(
        "/api/v1/teacher/quizzes",
        headers=student_headers,
    )
    assert forbidden.status_code == 403

    delete_response = await client.delete(
        f"/api/v1/teacher/quizzes/{created['id']}",
        headers=teacher_headers,
    )
    assert delete_response.status_code == 200, delete_response.text
