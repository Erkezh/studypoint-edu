from __future__ import annotations

import uuid

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.classroom import Classroom, Enrollment
from app.models.enums import UserRole
from app.repositories.catalog_repo import GradeRepository
from app.repositories.classroom_repo import ClassroomRepository
from app.repositories.user_repo import UserRepository
from app.schemas.classroom import ClassroomCreateRequest, ClassroomResponse
from app.utils.time import utc_now


class ClassroomService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.classrooms = ClassroomRepository(session)
        self.grades = GradeRepository(session)
        self.users = UserRepository(session)

    async def create_classroom(self, *, teacher_id: str, req: ClassroomCreateRequest) -> ClassroomResponse:
        teacher_uuid = _parse_uuid(teacher_id)
        grade = await self.grades.get(req.grade_id)
        if grade is None:
            raise AppError(status_code=404, code="not_found", message="Grade not found")

        classroom = Classroom(teacher_id=teacher_uuid, title=req.title, grade_id=req.grade_id)
        await self.classrooms.create(classroom)
        return ClassroomResponse(id=str(classroom.id), title=classroom.title, grade_id=classroom.grade_id)

    async def list_classrooms(self, *, teacher_id: str) -> list[ClassroomResponse]:
        teacher_uuid = _parse_uuid(teacher_id)
        rows = await self.classrooms.list_for_teacher(teacher_uuid)
        return [ClassroomResponse(id=str(c.id), title=c.title, grade_id=c.grade_id) for c in rows]

    async def enroll_student(self, *, teacher_id: str, classroom_id: str, student_id: str) -> None:
        teacher_uuid = _parse_uuid(teacher_id)
        classroom = await self.classrooms.get(classroom_id)
        if classroom is None or classroom.teacher_id != teacher_uuid:
            raise AppError(status_code=404, code="not_found", message="Classroom not found")

        student = await self.users.get_by_id(student_id)
        if student is None or student.role != UserRole.STUDENT:
            raise AppError(status_code=404, code="not_found", message="Student not found")

        try:
            await self.classrooms.enroll(
                Enrollment(
                    classroom_id=classroom.id,
                    student_id=student.id,
                    enrolled_at=utc_now(),
                )
            )
        except IntegrityError:
            return


def _parse_uuid(value: str) -> uuid.UUID:
    try:
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
    except ValueError as e:
        raise AppError(status_code=400, code="validation_error", message="Invalid id") from e
