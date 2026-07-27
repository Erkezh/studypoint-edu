import asyncio
import os
import sys
import json
from uuid import UUID

# Ensure PYTHONPATH is set
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.db.session import init_engine, get_sessionmaker
from app.services.quiz_service import QuizService
from app.schemas.quiz import QuizCreateRequest, QuizQuestionCreate
from app.models.enums import QuizQuestionOrder, QuizResultVisibility, QuizEndType
from sqlalchemy import text

async def main():
    print("=== Testing Quiz Visibility Control Logic ===")
    init_engine(settings.database_url)
    sm = get_sessionmaker()
    
    async with sm() as db:
        # Get a teacher user and student user
        res = await db.execute(text("SELECT id, role FROM users WHERE role='TEACHER' LIMIT 1"))
        teacher = res.fetchone()
        
        res = await db.execute(text("SELECT id, role FROM users WHERE role='STUDENT' LIMIT 1"))
        student = res.fetchone()

        if not teacher or not student:
            print("ERROR: Could not find teacher or student in DB to run test")
            return

        teacher_id = teacher[0]
        student_id = student[0]
        print(f"Teacher ID: {teacher_id}")
        print(f"Student ID: {student_id}")

        # Get a question ID
        res = await db.execute(text("SELECT id FROM questions LIMIT 1"))
        q_row = res.fetchone()
        if not q_row:
            print("ERROR: No questions found in DB")
            return
        question_id = q_row[0]

        service = QuizService(db)

        # Test 1: Quiz with HIDDEN visibility during active, ALWAYS after ended
        create_req1 = QuizCreateRequest(
            name="Test Quiz HIDDEN Active",
            question_order=QuizQuestionOrder.FIXED,
            result_visibility=QuizResultVisibility.HIDDEN,
            ended_result_visibility=QuizResultVisibility.ALWAYS,
            end_type=QuizEndType.MANUAL,
            questions=[QuizQuestionCreate(question_id=question_id, position=0)],
            student_ids=[student_id],
            is_draft=False
        )
        quiz1 = await service.create_quiz(teacher_id=teacher_id, req=create_req1)
        print(f"Created Quiz 1 (HIDDEN active, ALWAYS ended): {quiz1.id}")

        # Student lists assigned quizzes
        assigned = await service.list_assigned_quizzes(student_id=student_id)
        q1_assigned = next((a for a in assigned if a.quiz_id == quiz1.id), None)
        assert q1_assigned is not None, "Quiz 1 should be assigned"
        assert q1_assigned.quiz.result_visibility == QuizResultVisibility.HIDDEN
        print("✓ Verified Quiz 1 result_visibility is HIDDEN")

        # Test 2: Submit quiz 1 answer
        sub = await service.submit_quiz_assignment(
            student_id=student_id,
            assignment_id=q1_assigned.id,
            score=100,
            time_spent_seconds=45,
            question_results=[{"question_id": str(q1_assigned.quiz.questions[0].id), "submitted_answer": "test"}]
        )
        assert sub.score is not None, "Quiz 1 submission should produce score"
        print(f"✓ Submitted Quiz 1, score: {sub.score}%")

        # End Quiz 1 manually
        ended_assign = await service.end_quiz_assignment(q1_assigned.id)
        assert ended_assign.end_at is not None, "Quiz 1 should be ended"
        print("✓ Manually ended Quiz 1 assignment")

        # Re-fetch assigned quizzes and verify ended visibility
        assigned_after = await service.list_assigned_quizzes(student_id=student_id)
        q1_after = next((a for a in assigned_after if a.quiz_id == quiz1.id), None)
        assert q1_after.quiz.ended_result_visibility == QuizResultVisibility.ALWAYS
        print("✓ Verified Quiz 1 ended_result_visibility is ALWAYS after ending")

        print("=== ALL QUIZ VISIBILITY TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    asyncio.run(main())
