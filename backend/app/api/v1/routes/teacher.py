from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.schemas.base import ApiResponse
from app.services.analytics_service import AnalyticsService
from app.services.assignment_service import AssignmentService

router = APIRouter(dependencies=[Depends(require_roles("TEACHER"))])


@router.get("/analytics/classroom/{classroom_id}", response_model=ApiResponse[dict])
async def classroom_analytics(
    classroom_id: str,
    user=Depends(get_current_user),
    svc: AnalyticsService = Depends(),
):
    return ApiResponse(data=await svc.classroom_analytics(teacher_id=user.id, classroom_id=classroom_id))


@router.get("/classrooms/{classroom_id}/assignments/{assignment_id}/score-grid", response_model=ApiResponse[dict])
async def assignment_score_grid(
    classroom_id: str,
    assignment_id: str,
    user=Depends(get_current_user),
    svc: AssignmentService = Depends(),
):
    return ApiResponse(data=await svc.score_grid(teacher_id=user.id, classroom_id=classroom_id, assignment_id=assignment_id))
