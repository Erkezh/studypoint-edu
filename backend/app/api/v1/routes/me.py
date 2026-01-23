from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.schemas.assignment import StudentAssignmentResponse
from app.schemas.base import ApiResponse
from app.services.assignment_service import AssignmentService

router = APIRouter(dependencies=[Depends(require_roles("STUDENT"))])


@router.get("/assignments", response_model=ApiResponse[list[StudentAssignmentResponse]])
async def my_assignments(user=Depends(get_current_user), svc: AssignmentService = Depends()):
    return ApiResponse(data=await svc.list_my_assignments(student_id=user.id))


@router.get("/assignments/{assignment_id}", response_model=ApiResponse[StudentAssignmentResponse])
async def my_assignment(assignment_id: str, user=Depends(get_current_user), svc: AssignmentService = Depends()):
    return ApiResponse(data=await svc.get_my_assignment(student_id=user.id, assignment_id=assignment_id))

