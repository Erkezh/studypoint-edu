from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.schemas.assignment import AssignmentCreateRequest, AssignmentResponse
from app.schemas.base import ApiResponse
from app.services.assignment_service import AssignmentService

router = APIRouter()


@router.post("", response_model=ApiResponse[AssignmentResponse], dependencies=[Depends(require_roles("TEACHER"))])
async def create_assignment(
    body: AssignmentCreateRequest,
    user=Depends(get_current_user),
    svc: AssignmentService = Depends(),
):
    return ApiResponse(data=await svc.create_assignment(teacher_id=user.id, req=body))


@router.get("", response_model=ApiResponse[list[AssignmentResponse]], dependencies=[Depends(require_roles("TEACHER"))])
async def list_assignments(
    classroom_id: str | None = Query(default=None),
    user=Depends(get_current_user),
    svc: AssignmentService = Depends(),
):
    return ApiResponse(data=await svc.list_assignments(teacher_id=user.id, classroom_id=classroom_id))

