from __future__ import annotations
import pytest
import httpx
from app.models.enums import QuestionType

async def login(client: httpx.AsyncClient, email: str, password: str) -> dict:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]

@pytest.fixture
async def teacher_token(client: httpx.AsyncClient) -> str:
    data = await login(client, "teacher@example.com", "Password123!")
    return data["access_token"]

@pytest.fixture
async def student_token(client: httpx.AsyncClient) -> str:
    data = await login(client, "student@example.com", "Password123!")
    return data["access_token"]

@pytest.fixture
async def admin_token(client: httpx.AsyncClient) -> str:
    data = await login(client, "admin@example.com", "Password123!")
    return data["access_token"]

@pytest.mark.asyncio
async def test_quiz_grading_mcq_and_plugin(client, teacher_token, student_token, admin_token):
    # 1. Create a PLUGIN question using admin_token
    q_plugin = await client.post(
        "/api/v1/admin/questions",
        json={
            "skill_id": 1,
            "type": "PLUGIN",
            "prompt": "Solve addition using plugin",
            "data": {
                "plugin_id": "math-addition-example",
                "plugin_version": "1.0.0",
                "entry": "index.html"
            },
            "correct_answer": {},
            "explanation": "Solve addition",
            "level": 1,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert q_plugin.status_code == 200, q_plugin.text
    plugin_q_id = q_plugin.json()["data"]["id"]

    # 2. Create and assign a quiz as teacher
    quiz_res = await client.post(
        "/api/v1/teacher/quizzes",
        json={
            "name": "Grading Test Quiz",
            "question_order": "FIXED",
            "result_visibility": "ALWAYS",
            "ended_result_visibility": "ALWAYS",
            "end_type": "MANUAL",
            "questions": [
                {"question_id": 1, "position": 1},
                {"question_id": plugin_q_id, "position": 2}
            ],
            "is_draft": False,
            "student_ids": []
        },
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert quiz_res.status_code == 200, quiz_res.text
    quiz_data = quiz_res.json()["data"]
    quiz_id = quiz_data["id"]
    
    # 3. Get student assigned quizzes
    student_quizzes_res = await client.get(
        "/api/v1/student/quizzes/all",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert student_quizzes_res.status_code == 200, student_quizzes_res.text
    
    # Find our assignment and questions list
    assignments = []
    questions_list = []
    for qz in student_quizzes_res.json()["data"]:
        if qz["id"] == str(quiz_id):
            assignments = qz["assignments"]
            questions_list = qz["questions"]
            break
            
    assert len(assignments) > 0, "No assignments found for student"
    assignment_id = assignments[0]["id"]

    # Find the QuizQuestion.id (UUID) for each question
    qq_id_mcq = None
    qq_id_plugin = None
    for qq in questions_list:
        if qq["question_id"] == 1:
            qq_id_mcq = qq["id"]
        elif qq["question_id"] == plugin_q_id:
            qq_id_plugin = qq["id"]

    # 4. Submit student answers to the quiz using the QuizQuestion UUIDs
    submit_res = await client.post(
        f"/api/v1/student/quizzes/assignments/{assignment_id}/submit",
        json={
            "score": 100,
            "time_spent_seconds": 12,
            "question_results": [
                {
                    "question_id": str(qq_id_mcq),
                    "submitted_answer": {"id": "B", "text": "56"}
                },
                {
                    "question_id": str(qq_id_plugin),
                    "submitted_answer": {"isCorrect": True, "answer": 8, "question": "5 + 3 = ?"}
                }
            ]
        },
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert submit_res.status_code == 200, submit_res.text
    submitted_assignment = submit_res.json()["data"]
    
    # Assert score is 100% since both answers are correct!
    assert submitted_assignment["score"] == 100
    assert submitted_assignment["question_results"][str(qq_id_mcq)]["correct"] is True
    assert submitted_assignment["question_results"][str(qq_id_mcq)]["submitted_answer"] == "B"
    assert submitted_assignment["question_results"][str(qq_id_plugin)]["correct"] is True
    assert submitted_assignment["question_results"][str(qq_id_plugin)]["submitted_answer"]["answer"] == 8

@pytest.mark.asyncio
async def test_quiz_grading_mixed_correctness(client, teacher_token, student_token, admin_token):
    # 1. Create a PLUGIN question using admin_token
    q_plugin = await client.post(
        "/api/v1/admin/questions",
        json={
            "skill_id": 1,
            "type": "PLUGIN",
            "prompt": "Solve addition using plugin",
            "data": {
                "plugin_id": "math-addition-example",
                "plugin_version": "1.0.0",
                "entry": "index.html"
            },
            "correct_answer": {},
            "explanation": "Solve addition",
            "level": 1,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert q_plugin.status_code == 200, q_plugin.text
    plugin_q_id = q_plugin.json()["data"]["id"]

    # 2. Create and assign a quiz as teacher
    quiz_res = await client.post(
        "/api/v1/teacher/quizzes",
        json={
            "name": "Mixed Grading Test Quiz",
            "question_order": "FIXED",
            "result_visibility": "ALWAYS",
            "ended_result_visibility": "ALWAYS",
            "end_type": "MANUAL",
            "questions": [
                {"question_id": 1, "position": 1},
                {"question_id": plugin_q_id, "position": 2}
            ],
            "is_draft": False,
            "student_ids": []
        },
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert quiz_res.status_code == 200, quiz_res.text
    quiz_data = quiz_res.json()["data"]
    quiz_id = quiz_data["id"]
    
    # 3. Get student assigned quizzes
    student_quizzes_res = await client.get(
        "/api/v1/student/quizzes/all",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert student_quizzes_res.status_code == 200, student_quizzes_res.text
    
    # Find our assignment and questions list
    assignments = []
    questions_list = []
    for qz in student_quizzes_res.json()["data"]:
        if qz["id"] == str(quiz_id):
            assignments = qz["assignments"]
            questions_list = qz["questions"]
            break
            
    assert len(assignments) > 0, "No assignments found for student"
    assignment_id = assignments[0]["id"]

    # Find the QuizQuestion.id (UUID) for each question
    qq_id_mcq = None
    qq_id_plugin = None
    for qq in questions_list:
        if qq["question_id"] == 1:
            qq_id_mcq = qq["id"]
        elif qq["question_id"] == plugin_q_id:
            qq_id_plugin = qq["id"]

    # 4. Submit student answers: MCQ is INCORRECT (B is correct, we answer C), PLUGIN is CORRECT (isCorrect = True)
    submit_res = await client.post(
        f"/api/v1/student/quizzes/assignments/{assignment_id}/submit",
        json={
            "score": 100,
            "time_spent_seconds": 12,
            "question_results": [
                {
                    "question_id": str(qq_id_mcq),
                    "submitted_answer": {"id": "C", "text": "72"}
                },
                {
                    "question_id": str(qq_id_plugin),
                    "submitted_answer": {"isCorrect": True, "answer": 8, "question": "5 + 3 = ?"}
                }
            ]
        },
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert submit_res.status_code == 200, submit_res.text
    submitted_assignment = submit_res.json()["data"]
    
    # Assert score is 50%
    assert submitted_assignment["score"] == 50
    assert submitted_assignment["question_results"][str(qq_id_mcq)]["correct"] is False
    assert submitted_assignment["question_results"][str(qq_id_plugin)]["correct"] is True
