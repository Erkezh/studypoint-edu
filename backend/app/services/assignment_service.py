from __future__ import annotations

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.assignment import Assignment, AssignmentStatusRow
from app.models.enums import AssignmentStatus
from app.repositories.assignment_repo import AssignmentRepository, AssignmentStatusRepository
from app.repositories.classroom_repo import ClassroomRepository
from app.repositories.catalog_repo import SkillRepository
from app.models.user import User
from app.schemas.assignment import AssignmentCreateRequest, AssignmentResponse, AssignmentStatusResponse, StudentAssignmentResponse


class AssignmentService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.assignments = AssignmentRepository(session)
        self.status = AssignmentStatusRepository(session)
        self.classrooms = ClassroomRepository(session)
        self.skills = SkillRepository(session)

    async def create_assignment(self, *, teacher_id: str, req: AssignmentCreateRequest) -> AssignmentResponse:
        teacher_uuid = _parse_uuid(teacher_id)
        classroom = await self.classrooms.get(req.classroom_id)
        if classroom is None or classroom.teacher_id != teacher_uuid:
            raise AppError(status_code=404, code="not_found", message="Classroom not found")
        skill = await self.skills.get(req.skill_id)
        if skill is None:
            raise AppError(status_code=404, code="not_found", message="Skill not found")
        if req.target_smartscore not in {70, 80, 90, 100}:
            raise AppError(status_code=400, code="validation_error", message="target_smartscore must be one of 70/80/90/100")

        assignment = Assignment(
            classroom_id=classroom.id,
            skill_id=req.skill_id,
            due_at=req.due_at,
            target_smartscore=req.target_smartscore,
        )
        await self.assignments.create(assignment)
        enrollments = await self.classrooms.list_enrollments(classroom.id)
        for enr in enrollments:
            self.session.add(
                AssignmentStatusRow(
                    assignment_id=assignment.id,
                    student_id=enr.student_id,
                    status=AssignmentStatus.NOT_STARTED,
                )
            )
        await self.session.flush()
        return AssignmentResponse(
            id=str(assignment.id),
            classroom_id=str(assignment.classroom_id),
            skill_id=assignment.skill_id,
            due_at=assignment.due_at,
            target_smartscore=assignment.target_smartscore,
        )

    async def list_assignments(self, *, teacher_id: str, classroom_id: str | None) -> list[AssignmentResponse]:
        teacher_uuid = _parse_uuid(teacher_id)
        classroom_uuid = _parse_uuid(classroom_id) if classroom_id else None
        rows = await self.assignments.list_for_teacher(teacher_id=teacher_uuid, classroom_id=classroom_uuid)
        return [
            AssignmentResponse(
                id=str(a.id),
                classroom_id=str(a.classroom_id),
                skill_id=a.skill_id,
                due_at=a.due_at,
                target_smartscore=a.target_smartscore,
            )
            for a in rows
        ]

    async def list_my_assignments(self, *, student_id: str) -> list[StudentAssignmentResponse]:
        sid = _parse_uuid(student_id)
        rows = await self.assignments.list_for_student(student_id=sid)
        out: list[StudentAssignmentResponse] = []
        for a, s in rows:
            out.append(
                StudentAssignmentResponse(
                    assignment=AssignmentResponse(
                        id=str(a.id),
                        classroom_id=str(a.classroom_id),
                        skill_id=a.skill_id,
                        due_at=a.due_at,
                        target_smartscore=a.target_smartscore,
                    ),
                    status=AssignmentStatusResponse(
                        assignment_id=str(s.assignment_id),
                        student_id=str(s.student_id),
                        status=s.status.value if hasattr(s.status, "value") else str(s.status),
                        best_smartscore=s.best_smartscore,
                        last_smartscore=s.last_smartscore,
                        questions_answered=s.questions_answered,
                        time_spent_seconds=getattr(s, "time_spent_seconds", 0),
                        completed_at=s.completed_at,
                        last_activity_at=getattr(s, "last_activity_at", None),
                    ),
                )
            )
        return out

    async def get_my_assignment(self, *, student_id: str, assignment_id: str) -> StudentAssignmentResponse:
        sid = _parse_uuid(student_id)
        aid = _parse_uuid(assignment_id)
        rows = await self.assignments.list_for_student(student_id=sid)
        for a, s in rows:
            if a.id == aid:
                return StudentAssignmentResponse(
                    assignment=AssignmentResponse(
                        id=str(a.id),
                        classroom_id=str(a.classroom_id),
                        skill_id=a.skill_id,
                        due_at=a.due_at,
                        target_smartscore=a.target_smartscore,
                    ),
                    status=AssignmentStatusResponse(
                        assignment_id=str(s.assignment_id),
                        student_id=str(s.student_id),
                        status=s.status.value if hasattr(s.status, "value") else str(s.status),
                        best_smartscore=s.best_smartscore,
                        last_smartscore=s.last_smartscore,
                        questions_answered=s.questions_answered,
                        time_spent_seconds=getattr(s, "time_spent_seconds", 0),
                        completed_at=s.completed_at,
                        last_activity_at=getattr(s, "last_activity_at", None),
                    ),
                )
        raise AppError(status_code=404, code="not_found", message="Assignment not found")

    async def score_grid(
        self,
        *,
        teacher_id: str,
        classroom_id: str,
        assignment_id: str,
    ) -> dict:
        import sqlalchemy as sa

        tid = _parse_uuid(teacher_id)
        cid = _parse_uuid(classroom_id)
        aid = _parse_uuid(assignment_id)

        assignment = await self.assignments.get_for_teacher(assignment_id=aid, teacher_id=tid)
        if assignment is None or assignment.classroom_id != cid:
            raise AppError(status_code=404, code="not_found", message="Assignment not found")

        stmt = (
            sa.select(User, AssignmentStatusRow)
            .join(AssignmentStatusRow, AssignmentStatusRow.student_id == User.id)
            .where(AssignmentStatusRow.assignment_id == aid)
            .order_by(User.full_name.asc())
        )
        rows = (await self.session.execute(stmt)).all()
        grid = []
        for user, status_row in rows:
            grid.append(
                {
                    "student_id": str(user.id),
                    "full_name": user.full_name,
                    "email": user.email,
                    "status": status_row.status.value if hasattr(status_row.status, "value") else str(status_row.status),
                    "best_smartscore": status_row.best_smartscore,
                    "last_smartscore": status_row.last_smartscore,
                    "questions_answered": status_row.questions_answered,
                    "time_spent_seconds": getattr(status_row, "time_spent_seconds", 0),
                    "completed_at": status_row.completed_at,
                    "last_activity_at": getattr(status_row, "last_activity_at", None),
                }
            )

        summary = {"completed": 0, "in_progress": 0, "not_started": 0}
        for r in grid:
            if r["status"] == "COMPLETED":
                summary["completed"] += 1
            elif r["status"] == "IN_PROGRESS":
                summary["in_progress"] += 1
            else:
                summary["not_started"] += 1

        return {
            "assignment": {
                "id": str(assignment.id),
                "classroom_id": str(assignment.classroom_id),
                "skill_id": assignment.skill_id,
                "due_at": assignment.due_at,
                "target_smartscore": assignment.target_smartscore,
            },
            "summary": summary,
            "rows": grid,
        }



def _parse_uuid(value: str | None) -> uuid.UUID:
    if value is None:
        raise AppError(status_code=400, code="validation_error", message="Invalid id")
    try:
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
    except ValueError as e:
        raise AppError(status_code=400, code="validation_error", message="Invalid id") from e
