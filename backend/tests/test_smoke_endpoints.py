from __future__ import annotations

import uuid

import pytest


async def _login(client, email: str, password: str) -> dict:
    r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["data"]


@pytest.mark.asyncio
async def test_smoke_catalog_endpoints(client, student_token):
    r1 = await client.get("/api/v1/subjects")
    assert r1.status_code == 200, r1.text
    assert isinstance(r1.json()["data"], list)

    r2 = await client.get("/api/v1/grades")
    assert r2.status_code == 200, r2.text
    assert isinstance(r2.json()["data"], list)

    r3 = await client.get("/api/v1/skills", params={"subject_slug": "math", "grade_number": 5, "page": 1, "page_size": 10})
    assert r3.status_code == 200, r3.text
    assert "meta" in r3.json()

    # seeded skills include id=1
    r4 = await client.get("/api/v1/skills/1")
    assert r4.status_code == 200, r4.text

    # stats requires auth
    r5 = await client.get("/api/v1/skills/1/stats", headers={"Authorization": f"Bearer {student_token}"})
    assert r5.status_code == 200, r5.text


@pytest.mark.asyncio
async def test_smoke_practice_next_finish_and_questions_log(client, student_token, cleanup_practice_tables):
    start = await client.post(
        "/api/v1/practice/sessions",
        json={"skill_id": 1},
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "smoke-practice-start"},
    )
    assert start.status_code == 200, start.text
    sid = start.json()["data"]["id"]

    nxt = await client.post(f"/api/v1/practice/sessions/{sid}/next", headers={"Authorization": f"Bearer {student_token}"})
    assert nxt.status_code == 200, nxt.text

    hb = await client.post(
        f"/api/v1/practice/sessions/{sid}/heartbeat",
        json={"is_active": True, "focus": True, "interaction": True},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert hb.status_code == 200, hb.text

    sess = await client.get(f"/api/v1/practice/sessions/{sid}", headers={"Authorization": f"Bearer {student_token}"})
    assert sess.status_code == 200, sess.text
    q = sess.json()["data"]["current_question"]
    qid = q["id"]
    submitted = {"choice": "B"} if qid == 1 else {"value": 108}

    sub = await client.post(
        f"/api/v1/practice/sessions/{sid}/submit",
        json={"question_id": qid, "submitted_answer": submitted, "time_spent_sec": 1},
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "smoke-practice-submit"},
    )
    assert sub.status_code == 200, sub.text

    log = await client.get(
        "/api/v1/analytics/skills/1/questions-log",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert log.status_code == 200, log.text
    assert log.json()["data"]["skill_id"] == 1

    fin = await client.post(
        f"/api/v1/practice/sessions/{sid}/finish",
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "smoke-practice-finish"},
    )
    assert fin.status_code == 200, fin.text


@pytest.mark.asyncio
async def test_smoke_admin_crud_and_bulk_import(client, admin_token):
    # Subjects CRUD (create/update/delete)
    slug = f"sub-{uuid.uuid4().hex[:8]}"
    created = await client.post(
        "/api/v1/admin/subjects",
        json={"slug": slug, "title": "Temp Subject"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert created.status_code == 200, created.text
    subject_id = created.json()["data"]["id"]

    updated = await client.patch(
        f"/api/v1/admin/subjects/{subject_id}",
        json={"title": "Temp Subject Updated"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert updated.status_code == 200, updated.text

    # Grades list + update title of an existing grade (id=7 is grade 5 in seed)
    gl = await client.get("/api/v1/admin/grades", headers={"Authorization": f"Bearer {admin_token}"})
    assert gl.status_code == 200, gl.text
    gup = await client.patch(
        "/api/v1/admin/grades/7",
        json={"title": "5"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert gup.status_code == 200, gup.text

    # Skills CRUD
    scode = f"Z.{uuid.uuid4().hex[:4]}"
    sk = await client.post(
        "/api/v1/admin/skills",
        json={
            "subject_id": 1,
            "grade_id": 7,
            "code": scode,
            "title": "Temp Skill",
            "description": "Temp",
            "tags": ["temp"],
            "difficulty": 1,
            "is_published": True,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert sk.status_code == 200, sk.text
    skill_id = sk.json()["data"]["id"]

    sku = await client.patch(
        f"/api/v1/admin/skills/{skill_id}",
        json={"title": "Temp Skill Updated"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert sku.status_code == 200, sku.text

    # Questions CRUD
    q = await client.post(
        "/api/v1/admin/questions",
        json={
            "skill_id": skill_id,
            "type": "NUMERIC",
            "prompt": "Compute 2 + 3",
            "data": {"tolerance": 0},
            "correct_answer": {"value": 5},
            "explanation": "2+3=5",
            "level": 1,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert q.status_code == 200, q.text
    qid = q.json()["data"]["id"]

    qu = await client.patch(
        f"/api/v1/admin/questions/{qid}",
        json={"explanation": "Updated"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert qu.status_code == 200, qu.text

    # Bulk import endpoint (admin)
    bulk = await client.post(
        "/api/v1/admin/bulk_import",
        json={
            "skills": [
                {
                    "subject_id": 1,
                    "grade_id": 7,
                    "code": f"Y.{uuid.uuid4().hex[:4]}",
                    "title": "Bulk Skill",
                    "description": "Bulk",
                    "tags": [],
                    "difficulty": 1,
                    "is_published": True,
                }
            ],
            "questions": [],
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert bulk.status_code == 200, bulk.text

    # Cleanup created entities
    dq = await client.delete(f"/api/v1/admin/questions/{qid}", headers={"Authorization": f"Bearer {admin_token}"})
    assert dq.status_code == 200, dq.text
    ds = await client.delete(f"/api/v1/admin/skills/{skill_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert ds.status_code == 200, ds.text
    dd = await client.delete(f"/api/v1/admin/subjects/{subject_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert dd.status_code == 200, dd.text


@pytest.mark.asyncio
async def test_smoke_teacher_and_reports_and_awards(client, cleanup_practice_tables):
    teacher = await _login(client, "teacher@example.com", "Password123!")
    student = await _login(client, "student@example.com", "Password123!")
    admin = await _login(client, "admin@example.com", "Password123!")
    teacher_token = teacher["access_token"]
    student_token = student["access_token"]
    admin_token = admin["access_token"]

    # Create classroom
    classroom = await client.post(
        "/api/v1/classrooms",
        json={"title": f"Temp Class {uuid.uuid4().hex[:6]}", "grade_id": 7},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert classroom.status_code == 200, classroom.text
    classroom_id = classroom.json()["data"]["id"]

    # Enroll student
    enr = await client.post(
        f"/api/v1/classrooms/{classroom_id}/enroll",
        json={"student_id": student["user"]["id"]},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert enr.status_code == 200, enr.text

    # Create assignment + list assignments
    a = await client.post(
        "/api/v1/assignments",
        json={"classroom_id": classroom_id, "skill_id": 1, "due_at": None, "target_smartscore": 70},
        headers={"Authorization": f"Bearer {teacher_token}", "Idempotency-Key": "smoke-assign"},
    )
    assert a.status_code == 200, a.text
    assignment_id = a.json()["data"]["id"]

    al = await client.get("/api/v1/assignments", params={"classroom_id": classroom_id}, headers={"Authorization": f"Bearer {teacher_token}"})
    assert al.status_code == 200, al.text

    # Practice at least one attempt so PDFs have content
    # Ensure there are enough questions to avoid repeats
    for i in range(3):
        q = await client.post(
            "/api/v1/admin/questions",
            json={
                "skill_id": 1,
                "type": "NUMERIC",
                "prompt": f"Compute {10+i} + {10+i}.",
                "data": {"tolerance": 0},
                "correct_answer": {"value": (10 + i) * 2},
                "explanation": "seed",
                "level": 1,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert q.status_code == 200, q.text

    s = await client.post(
        "/api/v1/practice/sessions",
        json={"skill_id": 1},
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "smoke-report-session"},
    )
    assert s.status_code == 200, s.text
    session_id = s.json()["data"]["id"]
    qid = s.json()["data"]["current_question"]["id"]
    submitted = {"choice": "B"} if qid == 1 else {"value": 108} if qid == 2 else {"value": 20}
    sub = await client.post(
        f"/api/v1/practice/sessions/{session_id}/submit",
        json={"question_id": qid, "submitted_answer": submitted, "time_spent_sec": 1},
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "smoke-report-submit"},
    )
    assert sub.status_code == 200, sub.text

    # Teacher analytics
    ta = await client.get(f"/api/v1/teacher/analytics/classroom/{classroom_id}", headers={"Authorization": f"Bearer {teacher_token}"})
    assert ta.status_code == 200, ta.text

    # Score grid
    sg = await client.get(
        f"/api/v1/teacher/classrooms/{classroom_id}/assignments/{assignment_id}/score-grid",
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert sg.status_code == 200, sg.text

    # Student analytics endpoints
    ov = await client.get("/api/v1/analytics/overview", headers={"Authorization": f"Bearer {student_token}"})
    assert ov.status_code == 200, ov.text

    sk = await client.get("/api/v1/analytics/skills", headers={"Authorization": f"Bearer {student_token}"})
    assert sk.status_code == 200, sk.text

    # PDFs
    pdf1 = await client.get(f"/api/v1/reports/practice-sessions/{session_id}.pdf", headers={"Authorization": f"Bearer {student_token}"})
    assert pdf1.status_code == 200
    assert pdf1.headers["content-type"].startswith("application/pdf")
    assert len(pdf1.content) > 1000

    pdf2 = await client.get(f"/api/v1/reports/assignments/{assignment_id}.pdf", headers={"Authorization": f"Bearer {teacher_token}"})
    assert pdf2.status_code == 200
    assert pdf2.headers["content-type"].startswith("application/pdf")
    assert len(pdf2.content) > 1000

    # Certificate
    cert = await client.get(
        "/api/v1/awards/certificates/EXCELLENCE.pdf",
        params={"skill_id": 1},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert cert.status_code == 200
    assert cert.headers["content-type"].startswith("application/pdf")
    assert len(cert.content) > 1000

