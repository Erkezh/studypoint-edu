from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.base import ApiResponse
from app.schemas.quiz import QuizResponse
from app.services.quiz_service import QuizService

router = APIRouter()


@router.get("/all", response_model=ApiResponse[list[QuizResponse]])
async def list_all_quizzes_for_student(
    user=Depends(get_current_user),
    svc: QuizService = Depends(),
):
    """Return all quizzes created by any teacher (visible to all students)."""
    quizzes = await svc.list_all_quizzes()
    return ApiResponse(data=quizzes)
