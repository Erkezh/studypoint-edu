from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.errors import AppError
from app.core.rbac import require_roles
from app.schemas.base import ApiResponse
from app.schemas.teacher import TeacherCreateStudentRequest, TeacherCreateStudentResponse
from app.services.analytics_service import AnalyticsService
from app.services.assignment_service import AssignmentService
from app.services.presence_service import get_active_students
from app.services.teacher_scope import list_teacher_scoped_students, teacher_can_access_student
from app.services.teacher_service import TeacherService
from app.services.catalog_service import CatalogService
from app.models.user import User
from app.models.profile import StudentProfile
from app.models.classroom import Enrollment
from app.models.catalog import Grade, Skill
from app.models.topic import Topic
from app.models.question import Question
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
    scoped_students = await list_teacher_scoped_students(svc.session, teacher_id=user.id)
    student_ids = [str(student.id) for student in scoped_students]
    student_names = {str(student.id): student.full_name for student in scoped_students}
    total_students = len(scoped_students)

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

    active_ids = {entry["student_id"] for entry in active_list}
    inactive_students = [
        {
            "student_id": str(student.id),
            "full_name": student.full_name,
        }
        for student in scoped_students
        if str(student.id) not in active_ids
    ]

    active_count = len(active_list)
    return ApiResponse(data={
        "active_count": active_count,
        "inactive_count": len(inactive_students),
        "needs_help_count": needs_help_count,
        "total_students": total_students,
        "students": active_list,
        "inactive_students": inactive_students,
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
    student_uuid = _parse_uuid(student_id)
    if not await teacher_can_access_student(teacher_svc.session, teacher_id=user.id, student_id=student_uuid):
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
    if not await teacher_can_access_student(svc.session, teacher_id=user.id, student_id=student_uuid):
        raise AppError(status_code=403, code="forbidden", message="Not your student")

    stmt = select(User).where(User.id == student_uuid)
    student = (await svc.session.execute(stmt)).scalar_one_or_none()
    if not student:
        raise AppError(status_code=404, code="not_found", message="Student not found")

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
    if not await teacher_can_access_student(svc.session, teacher_id=user.id, student_id=student_uuid):
        raise AppError(status_code=403, code="forbidden", message="Not your student")

    # Use raw SQL DELETE — ORM delete() fails because student_profiles.user_id is a PK
    # and SQLAlchemy tries to null it before cascade-deleting (which is illegal).
    # The DB has ON DELETE CASCADE on student_profiles.user_id so raw DELETE works fine.
    await svc.session.execute(sql_delete(User).where(User.id == student_uuid))
    await svc.session.flush()
    return ApiResponse(data={"deleted": student_id})


@router.get("/catalog/grades/{grade_num}/topics", response_model=ApiResponse[list[dict]])
async def list_grade_topics(
    grade_num: int,
    user=Depends(get_current_user),
    svc: TeacherService = Depends(),
):
    """List topics that have skills in a specific grade."""
    # First find grade_id
    grade_stmt = select(Grade.id).where(Grade.number == grade_num)
    grade_id = (await svc.session.execute(grade_stmt)).scalar_one_or_none()
    if not grade_id:
        raise AppError(status_code=404, code="not_found", message="Grade not found")

    stmt = (
        select(Topic.id, Topic.title, Topic.description)
        .distinct()
        .join(Skill, Skill.topic_id == Topic.id)
        .where(Skill.grade_id == grade_id)
        .order_by(Topic.title)
    )
    rows = (await svc.session.execute(stmt)).all()
    return ApiResponse(data=[{"id": r.id, "title": r.title, "description": r.description} for r in rows])


@router.get("/catalog/topics/{topic_id}/questions", response_model=ApiResponse[list[dict]])
async def browse_catalog_questions(
    topic_id: int,
    user=Depends(get_current_user),
    svc: TeacherService = Depends(),
):
    """List questions for a specific topic across skills in that topic."""
    stmt = (
        select(Question)
        .join(Skill, Question.skill_id == Skill.id)
        .where(Skill.topic_id == topic_id)
        .order_by(Question.id)
    )
    result = await svc.session.execute(stmt)
    questions = result.scalars().all()
    
    return ApiResponse(data=[
        {
            "id": q.id,
            "type": q.type,
            "prompt": q.prompt,
            "level": q.level,
            "explanation": q.explanation
        } for q in questions
    ])


@router.get("/catalog/skills/{skill_id}/questions", response_model=ApiResponse[list[dict]])
async def browse_skill_questions(
    skill_id: int,
    user=Depends(get_current_user),
    svc: TeacherService = Depends(),
):
    """List questions for a specific skill."""
    stmt = (
        select(Question)
        .where(Question.skill_id == skill_id)
        .order_by(Question.id)
    )
    result = await svc.session.execute(stmt)
    questions = result.scalars().all()
    
    return ApiResponse(data=[
        {
            "id": q.id,
            "type": q.type,
            "prompt": q.prompt,
            "level": q.level,
            "explanation": q.explanation
        } for q in questions
    ])
