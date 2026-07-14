from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.base import ApiResponse
from app.schemas.quiz import QuizResponse
from app.services.quiz_service import QuizService

import uuid
from pydantic import BaseModel
from app.schemas.quiz import QuizAssignmentResponse

router = APIRouter()


class QuizSubmitRequest(BaseModel):
    score: int
    time_spent_seconds: int
    question_results: list[bool] | dict


@router.get("/all", response_model=ApiResponse[list[QuizResponse]])
async def list_all_quizzes_for_student(
    user=Depends(get_current_user),
    svc: QuizService = Depends(),
):
    """Return quizzes assigned to the current student."""
    assignments = await svc.list_assigned_quizzes(user.id)
    quizzes = []
    for a in assignments:
        if a.quiz:
            quiz = a.quiz
            quiz.assignments = [a]
            quizzes.append(quiz)
    return ApiResponse(data=quizzes)


@router.post("/assignments/{assignment_id}/submit", response_model=ApiResponse[QuizAssignmentResponse])
async def submit_student_quiz(
    assignment_id: uuid.UUID,
    body: QuizSubmitRequest,
    user=Depends(get_current_user),
    svc: QuizService = Depends(),
):
    assignment = await svc.submit_quiz_assignment(
        student_id=user.id,
        assignment_id=assignment_id,
        score=body.score,
        time_spent_seconds=body.time_spent_seconds,
        question_results=body.question_results
    )
    if not assignment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Assignment not found or unauthorized")
    return ApiResponse(data=assignment)
