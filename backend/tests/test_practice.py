from __future__ import annotations


async def test_practice_session_and_submit_updates_smartscore(client, student_token, cleanup_practice_tables):
    start = await client.post(
        "/api/v1/practice/sessions",
        json={"skill_id": 1},
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "start-1"},
    )
    assert start.status_code == 200, start.text
    payload = start.json()["data"]
    session_id = payload["id"]
    q = payload["current_question"]
    assert q and q["id"]

    expected = {
        1: {"choice": "B"},   # 7×8
        2: {"value": 108},    # 12×9
    }
    submitted_answer = expected.get(q["id"])
    assert submitted_answer is not None, f"Unexpected seeded question id: {q['id']}"

    submit = await client.post(
        f"/api/v1/practice/sessions/{session_id}/submit",
        json={"question_id": q["id"], "submitted_answer": submitted_answer, "time_spent_sec": 5},
        headers={"Authorization": f"Bearer {student_token}", "Idempotency-Key": "submit-1"},
    )
    assert submit.status_code == 200, submit.text
    res = submit.json()["data"]
    assert res["is_correct"] is True
    assert res["session"]["questions_answered"] == 1
    assert res["session"]["smartscore"] > 0
    assert res["next_question"] is not None
