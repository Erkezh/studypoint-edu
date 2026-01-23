from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.base import ApiResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview", response_model=ApiResponse[dict])
async def overview(user=Depends(get_current_user), svc: AnalyticsService = Depends()):
    return ApiResponse(data=await svc.overview(user_id=user.id))


@router.get("/skills", response_model=ApiResponse[list[dict]])
async def skills(user=Depends(get_current_user), svc: AnalyticsService = Depends()):
    return ApiResponse(data=await svc.skills(user_id=user.id))


@router.get("/skills/{skill_id}/questions-log", response_model=ApiResponse[dict])
async def questions_log(
    skill_id: int,
    student_id: str | None = None,
    user=Depends(get_current_user),
    svc: AnalyticsService = Depends(),
):
    role_value = getattr(user.role, "value", user.role)
    return ApiResponse(
        data=await svc.questions_log(
            requester_id=user.id,
            requester_role=role_value,
            skill_id=skill_id,
            student_id=student_id,
        )
    )


@router.get("/all-questions", response_model=ApiResponse[list[dict]])
async def all_questions(user=Depends(get_current_user), svc: AnalyticsService = Depends()):
    return ApiResponse(data=await svc.all_questions(user_id=user.id))
