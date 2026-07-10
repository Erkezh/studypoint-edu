from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.schemas.base import ApiResponse
from app.schemas.quiz import QuizCreateRequest, QuizResponse, QuizAssignmentCreate, QuizAssignmentResponse
from app.services.quiz_service import QuizService

router = APIRouter(dependencies=[Depends(require_roles("TEACHER"))])


@router.post("", response_model=ApiResponse[QuizResponse])
async def create_quiz(
    body: QuizCreateRequest,
    user=Depends(get_current_user),
    svc: QuizService = Depends(),
):
    return ApiResponse(data=await svc.create_quiz(teacher_id=user.id, req=body))

@router.put("/{quiz_id}", response_model=ApiResponse[QuizResponse])
async def update_quiz(
    quiz_id: uuid.UUID,
    body: QuizCreateRequest,
    user=Depends(get_current_user),
    svc: QuizService = Depends(),
):
    return ApiResponse(data=await svc.update_quiz(teacher_id=user.id, quiz_id=quiz_id, req=body))


@router.get("", response_model=ApiResponse[list[QuizResponse]])
async def list_quizzes(
    user=Depends(get_current_user),
    svc: QuizService = Depends(),
):
    return ApiResponse(data=await svc.list_quizzes(teacher_id=user.id))


@router.post("/assign", response_model=ApiResponse[QuizAssignmentResponse])
async def assign_quiz(
    body: QuizAssignmentCreate,
    user=Depends(get_current_user),
    svc: QuizService = Depends(),
):
    # In a real app, verify quiz belongs to teacher
    return ApiResponse(data=await svc.assign_quiz(req=body))

@router.delete("/{quiz_id}", response_model=ApiResponse[bool])
async def delete_quiz(
    quiz_id: uuid.UUID,
    user=Depends(get_current_user),
    svc: QuizService = Depends(),
):
    success = await svc.delete_quiz(teacher_id=user.id, quiz_id=quiz_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Quiz not found")
    return ApiResponse(data=True)


@router.post("/assignments/{assignment_id}/end", response_model=ApiResponse[QuizAssignmentResponse])
async def end_quiz_assignment(
    assignment_id: uuid.UUID,
    user=Depends(get_current_user),
    svc: QuizService = Depends(),
):
    assignment = await svc.end_quiz_assignment(assignment_id)
    if not assignment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Quiz assignment not found")
    return ApiResponse(data=assignment)
