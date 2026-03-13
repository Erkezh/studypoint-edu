from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.schemas.base import ApiResponse
from app.schemas.teacher import TeacherCreateStudentRequest, TeacherCreateStudentResponse
from app.services.analytics_service import AnalyticsService
from app.services.assignment_service import AssignmentService
from app.services.teacher_service import TeacherService
from app.models.user import User
from sqlalchemy import select

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


@router.post("/students", response_model=ApiResponse[TeacherCreateStudentResponse])
async def create_student(
    body: TeacherCreateStudentRequest,
    user=Depends(get_current_user),
    svc: TeacherService = Depends(),
):
    return ApiResponse(data=await svc.create_student(teacher_id=user.id, req=body))


@router.get("/students", response_model=ApiResponse[list[dict]])
async def get_students(
    user=Depends(get_current_user),
    svc: TeacherService = Depends(),
):
    # Retrieve students linked to this teacher
    stmt = select(User).where(User.teacher_id == user.id).order_by(User.full_name)
    students = (await svc.session.execute(stmt)).scalars().all()
    
    data = []
    for s in students:
        classrooms = [
            str(e.classroom_id) 
            for e in s.enrollments
        ] if hasattr(s, 'enrollments') else []
        
        data.append({
            "id": str(s.id),
            "full_name": s.full_name,
            "username": s.email,
            "classrooms": classrooms,
            "grade_level": s.profile.grade_level if hasattr(s, 'profile') and s.profile else None
        })
    return ApiResponse(data=data)
