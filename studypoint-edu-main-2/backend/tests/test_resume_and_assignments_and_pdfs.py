from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def _login(client, email: str, password: str) -> dict:
    r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["data"]


@pytest.mark.asyncio
async def test_resume_returns_same_session_and_question(client, student_token, cleanup_practice_tables):
    r1 = await client.post(
        "/api/v1/practice/sessions",
        json={"skill_id": 1},
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "resume-start-1"},
    )
    assert r1.status_code == 200, r1.text
    d1 = r1.json()["data"]
    sid1 = d1["id"]
    q1 = d1["current_question"]["id"]

    r2 = await client.post(
        "/api/v1/practice/sessions",
        json={"skill_id": 1},
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "resume-start-2"},
    )
    assert r2.status_code == 200, r2.text
    d2 = r2.json()["data"]
    assert d2["id"] == sid1
    assert d2["current_question"]["id"] == q1


@pytest.mark.asyncio
async def test_timer_inactivity_is_capped(client, student_token, cleanup_practice_tables):
    start = await client.post(
        "/api/v1/practice/sessions",
        json={"skill_id": 1},
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "timer-start"},
    )
    assert start.status_code == 200, start.text
    sid = start.json()["data"]["id"]

    from app.core.config import settings

    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        # Force last_activity_at far in the past.
        await conn.execute(
            text(
                "UPDATE practice_sessions SET last_activity_at = (now() - interval '1000 seconds'), active_time_seconds = 0 WHERE id = :id"
            ),
            {"id": sid},
        )
    await engine.dispose()

    hb = await client.post(
        f"/api/v1/practice/sessions/{sid}/heartbeat",
        json={"is_active": True, "focus": True, "interaction": True},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert hb.status_code == 200, hb.text
    active_time = hb.json()["data"]["active_time_seconds"]
    threshold = hb.json()["data"]["inactivity_threshold_seconds"]
    assert active_time == threshold


@pytest.mark.asyncio
async def test_assignment_completes_at_target_smartscore_and_pdfs_work(client, cleanup_practice_tables):
    teacher = await _login(client, "teacher@example.com", "Password123!")
    student = await _login(client, "student@example.com", "Password123!")
    admin = await _login(client, "admin@example.com", "Password123!")
    teacher_token = teacher["access_token"]
    student_token_local = student["access_token"]
    admin_token = admin["access_token"]

    # Get demo classroom
    cls = await client.get("/api/v1/classrooms", headers={"Authorization": f"Bearer {teacher_token}"})
    assert cls.status_code == 200, cls.text
    classroom_id = cls.json()["data"][0]["id"]

    # Ensure enough questions exist for skill 1 to avoid session-level repeats (unique attempt constraint).
    answer_key = {1: {"choice": "B"}, 2: {"value": 108}}
    for i in range(1, 21):
        q = await client.post(
            "/api/v1/admin/questions",
            json={
                "skill_id": 1,
                "type": "NUMERIC",
                "prompt": f"Compute {i} + {i}.",
                "data": {"tolerance": 0},
                "correct_answer": {"value": i + i},
                "explanation": f"{i}+{i}={i+i}",
                "level": 1,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert q.status_code == 200, q.text
        qid = q.json()["data"]["id"]
        answer_key[qid] = {"value": i + i}

    # Create assignment with easy target
    a = await client.post(
        "/api/v1/assignments",
        json={"classroom_id": classroom_id, "skill_id": 1, "due_at": None, "target_smartscore": 70},
        headers={"Authorization": f"Bearer {teacher_token}", "Idempotency-Key": "assign-1"},
    )
    assert a.status_code == 200, a.text
    assignment_id = a.json()["data"]["id"]

    # Practice until we reach target (limited questions in seed; repeats allowed)
    start = await client.post(
        "/api/v1/practice/sessions",
        json={"skill_id": 1},
        headers={"Authorization": f"Bearer {student_token_local}", "Idempotency-Key": "assign-practice-start"},
    )
    assert start.status_code == 200, start.text
    sid = start.json()["data"]["id"]

    current_score = start.json()["data"].get("current_smartscore") or 0

    for i in range(30):
        sess = await client.get(f"/api/v1/practice/sessions/{sid}", headers={"Authorization": f"Bearer {student_token_local}"})
        q = sess.json()["data"]["current_question"]
        qid = q["id"]
        submitted = answer_key.get(qid)
        assert submitted is not None, f"Unexpected question id {qid}"
        sub = await client.post(
            f"/api/v1/practice/sessions/{sid}/submit",
            json={"question_id": qid, "submitted_answer": submitted, "time_spent_sec": 1},
            headers={"Authorization": f"Bearer {student_token_local}", "Idempotency-Key": f"assign-submit-{i}"},
        )
        assert sub.status_code == 200, sub.text
        current_score = sub.json()["data"]["session"]["current_smartscore"] or 0
        if current_score >= 70:
            break

    my = await client.get("/api/v1/me/assignments", headers={"Authorization": f"Bearer {student_token_local}"})
    assert my.status_code == 200, my.text
    row = next(x for x in my.json()["data"] if x["assignment"]["id"] == assignment_id)
    assert row["status"]["status"] == "COMPLETED"

    # PDFs return application/pdf
    pdf1 = await client.get(
        f"/api/v1/reports/practice-sessions/{sid}.pdf",
        headers={"Authorization": f"Bearer {student_token_local}"},
    )
    assert pdf1.status_code == 200
    assert pdf1.headers["content-type"].startswith("application/pdf")
    assert len(pdf1.content) > 1000

    pdf2 = await client.get(
        f"/api/v1/reports/assignments/{assignment_id}.pdf",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert pdf2.status_code == 200
    assert pdf2.headers["content-type"].startswith("application/pdf")
    assert len(pdf2.content) > 1000
