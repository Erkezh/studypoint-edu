from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.schemas.base import ApiResponse
from app.schemas.classroom import (
    ClassroomCreateRequest,
    ClassroomEnrollRequest,
    ClassroomResponse,
)
from app.services.classroom_service import ClassroomService

router = APIRouter()


@router.post("", response_model=ApiResponse[ClassroomResponse], dependencies=[Depends(require_roles("TEACHER"))])
async def create_classroom(
    body: ClassroomCreateRequest,
    user=Depends(get_current_user),
    svc: ClassroomService = Depends(),
):
    return ApiResponse(data=await svc.create_classroom(teacher_id=user.id, req=body))


@router.get("", response_model=ApiResponse[list[ClassroomResponse]], dependencies=[Depends(require_roles("TEACHER"))])
async def list_classrooms(user=Depends(get_current_user), svc: ClassroomService = Depends()):
    return ApiResponse(data=await svc.list_classrooms(teacher_id=user.id))


@router.post("/{classroom_id}/enroll", response_model=ApiResponse[dict], dependencies=[Depends(require_roles("TEACHER"))])
async def enroll(
    classroom_id: str,
    body: ClassroomEnrollRequest,
    user=Depends(get_current_user),
    svc: ClassroomService = Depends(),
):
    await svc.enroll_student(teacher_id=user.id, classroom_id=classroom_id, student_id=body.student_id)
    return ApiResponse(data={"ok": True})

