from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.classroom import Classroom, Enrollment
from app.models.enums import UserRole
from app.models.user import User


@dataclass(frozen=True, slots=True)
class TeacherScopedStudent:
    id: uuid.UUID
    full_name: str


def _teacher_student_scope_stmt(*, teacher_id: uuid.UUID):
    enrolled_student_ids = (
        select(Enrollment.student_id)
        .join(Classroom, Classroom.id == Enrollment.classroom_id)
        .where(Classroom.teacher_id == teacher_id)
    )
    return (
        select(User.id, User.full_name)
        .where(
            User.role == UserRole.STUDENT,
            (User.teacher_id == teacher_id) | (User.id.in_(enrolled_student_ids)),
        )
    )


async def list_teacher_scoped_students(
    session: AsyncSession,
    *,
    teacher_id: uuid.UUID,
) -> list[TeacherScopedStudent]:
    """Return the deduplicated student scope visible to a teacher."""
    stmt = (
        _teacher_student_scope_stmt(teacher_id=teacher_id)
        .order_by(User.full_name, User.id)
    )
    rows = (await session.execute(stmt)).all()
    return [TeacherScopedStudent(id=row.id, full_name=row.full_name) for row in rows]


async def teacher_can_access_student(
    session: AsyncSession,
    *,
    teacher_id: uuid.UUID,
    student_id: uuid.UUID,
) -> bool:
    stmt = _teacher_student_scope_stmt(teacher_id=teacher_id).where(User.id == student_id)
    return (await session.execute(stmt.limit(1))).first() is not None
