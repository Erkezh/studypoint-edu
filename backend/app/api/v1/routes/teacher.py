from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.errors import AppError
from app.core.rbac import require_roles
from app.schemas.base import ApiResponse
from app.schemas.teacher import TeacherCreateStudentRequest, TeacherCreateStudentResponse
from app.services.analytics_service import AnalyticsService
from app.services.assignment_service import AssignmentService
from app.services.teacher_service import TeacherService
from app.services.presence_service import get_active_students
from app.models.user import User
from app.models.profile import StudentProfile
from app.models.classroom import Enrollment
from sqlalchemy import select, outerjoin

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
    # Use explicit LEFT JOINs to avoid async lazy-loading issues
    stmt = (
        select(
            User.id,
            User.full_name,
            User.email,
            StudentProfile.grade_level,
            StudentProfile.plain_password,
        )
        .select_from(
            outerjoin(User, StudentProfile, User.id == StudentProfile.user_id)
        )
        .where(User.teacher_id == user.id)
        .order_by(User.full_name)
    )
    rows = (await svc.session.execute(stmt)).all()

    data = []
    for row in rows:
        student_id = row.id
        # Fetch enrollments separately per student
        enrollments_stmt = select(Enrollment.classroom_id).where(Enrollment.student_id == student_id)
        enrollments = (await svc.session.execute(enrollments_stmt)).scalars().all()
        data.append({
            "id": str(student_id),
            "full_name": row.full_name,
            "username": row.email,
            "classrooms": [str(c) for c in enrollments],
            "grade_level": row.grade_level,
            "password": row.plain_password or "—",
        })
    return ApiResponse(data=data)

@router.get("/analytics/quickview", response_model=ApiResponse[dict])
async def teacher_quickview_analytics(
    include_questions: bool = False,
    user=Depends(get_current_user),
    svc: AnalyticsService = Depends(),
):
    data = await svc.teacher_quickview(teacher_id=user.id, include_questions=include_questions)
    return ApiResponse(data=data)


@router.get("/analytics/quickview/questions", response_model=ApiResponse[list[dict]])
async def teacher_quickview_questions(
    user=Depends(get_current_user),
    svc: AnalyticsService = Depends(),
):
    return ApiResponse(data=await svc.teacher_quickview_questions(teacher_id=user.id))


@router.get("/live-students", response_model=ApiResponse[dict])
async def get_live_students(
    user=Depends(get_current_user),
    svc: TeacherService = Depends(),
):
    """Return students who are currently practicing (have an active presence in Redis)."""
    # Get this teacher's student IDs
    stmt = select(User.id, User.full_name).where(User.teacher_id == user.id).order_by(User.full_name)
    rows = (await svc.session.execute(stmt)).all()

    student_ids = [str(row.id) for row in rows]
    student_names = {str(row.id): row.full_name for row in rows}
    total_students = len(student_ids)

    # Check Redis presence for each student
    active_list = await get_active_students(student_ids)

    # Enrich with full_name
    for entry in active_list:
        entry["full_name"] = student_names.get(entry["student_id"], "Unknown")

    # Count needs-help: SmartScore < 30 AND wrong > 3
    needs_help_count = sum(
        1 for s in active_list
        if s.get("smartscore", 0) < 30 and s.get("wrong", 0) > 3
    )

    active_count = len(active_list)
    return ApiResponse(data={
        "active_count": active_count,
        "inactive_count": total_students - active_count,
        "needs_help_count": needs_help_count,
        "total_students": total_students,
        "students": active_list,
    })


@router.get("/students/{student_id}/analytics", response_model=ApiResponse[dict])
async def student_analytics(
    student_id: str,
    include_questions: bool = True,
    user=Depends(get_current_user),
    svc: AnalyticsService = Depends(),
    teacher_svc: TeacherService = Depends(),
):
    from app.services.analytics_service import _parse_uuid
    # Verify student belongs to this teacher
    stmt = select(User).where(User.id == _parse_uuid(student_id), User.teacher_id == user.id)
    student = (await teacher_svc.session.execute(stmt)).scalar_one_or_none()
    if not student:
        raise AppError(status_code=403, code="forbidden", message="Not your student")

    overview = await svc.overview(user_id=student_id)
    skills = await svc.skills(user_id=student_id)
    all_questions = await svc.all_questions(user_id=student_id) if include_questions else []

    return ApiResponse(data={"overview": overview, "skills": skills, "all_questions": all_questions})


@router.post("/students/{student_id}/reset-password", response_model=ApiResponse[dict])
async def reset_student_password(
    student_id: str,
    user=Depends(get_current_user),
    svc: TeacherService = Depends(),
):
    from app.services.analytics_service import _parse_uuid
    from app.core.security import hash_password
    from app.services.teacher_service import _generate_password

    student_uuid = _parse_uuid(student_id)
    stmt = select(User).where(User.id == student_uuid, User.teacher_id == user.id)
    student = (await svc.session.execute(stmt)).scalar_one_or_none()
    if not student:
        raise AppError(status_code=403, code="forbidden", message="Not your student")

    new_password = _generate_password()
    student.password_hash = hash_password(new_password)

    profile_stmt = select(StudentProfile).where(StudentProfile.user_id == student_uuid)
    profile = (await svc.session.execute(profile_stmt)).scalar_one_or_none()
    if profile:
        profile.plain_password = new_password

    await svc.session.flush()
    return ApiResponse(data={"username": student.email, "password": new_password})


@router.delete("/students/{student_id}", response_model=ApiResponse[dict])
async def delete_student(
    student_id: str,
    user=Depends(get_current_user),
    svc: TeacherService = Depends(),
):
    from app.services.analytics_service import _parse_uuid
    from sqlalchemy import delete as sql_delete

    student_uuid = _parse_uuid(student_id)
    # Verify student belongs to this teacher
    stmt = select(User).where(User.id == student_uuid, User.teacher_id == user.id)
    student = (await svc.session.execute(stmt)).scalar_one_or_none()
    if not student:
        raise AppError(status_code=403, code="forbidden", message="Not your student")

    # Use raw SQL DELETE — ORM delete() fails because student_profiles.user_id is a PK
    # and SQLAlchemy tries to null it before cascade-deleting (which is illegal).
    # The DB has ON DELETE CASCADE on student_profiles.user_id so raw DELETE works fine.
    await svc.session.execute(sql_delete(User).where(User.id == student_uuid))
    await svc.session.flush()
    return ApiResponse(data={"deleted": student_id})
