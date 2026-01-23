from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment import Assignment, AssignmentStatusRow
from app.models.enums import AssignmentStatus
from app.models.classroom import Classroom


class AssignmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, assignment: Assignment) -> Assignment:
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def list_for_teacher(self, *, teacher_id: uuid.UUID, classroom_id: uuid.UUID | None) -> list[Assignment]:
        stmt = select(Assignment).join(Classroom, Classroom.id == Assignment.classroom_id).where(Classroom.teacher_id == teacher_id)
        if classroom_id is not None:
            stmt = stmt.where(Assignment.classroom_id == classroom_id)
        stmt = stmt.order_by(Assignment.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def get(self, assignment_id: str) -> Assignment | None:
        try:
            aid = uuid.UUID(assignment_id)
        except ValueError:
            return None
        return await self.session.get(Assignment, aid)

    async def get_for_teacher(self, *, assignment_id: uuid.UUID, teacher_id: uuid.UUID) -> Assignment | None:
        stmt = (
            select(Assignment)
            .join(Classroom, Classroom.id == Assignment.classroom_id)
            .where(Assignment.id == assignment_id, Classroom.teacher_id == teacher_id)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_for_student(self, *, student_id: uuid.UUID) -> list[tuple[Assignment, AssignmentStatusRow]]:
        stmt = (
            select(Assignment, AssignmentStatusRow)
            .join(AssignmentStatusRow, AssignmentStatusRow.assignment_id == Assignment.id)
            .where(AssignmentStatusRow.student_id == student_id)
            .order_by(Assignment.created_at.desc())
        )
        return list((await self.session.execute(stmt)).all())

    async def list_active_for_student_skill(
        self, *, student_id: uuid.UUID, skill_id: int
    ) -> list[tuple[Assignment, AssignmentStatusRow]]:
        stmt = (
            select(Assignment, AssignmentStatusRow)
            .join(AssignmentStatusRow, AssignmentStatusRow.assignment_id == Assignment.id)
            .where(
                Assignment.skill_id == skill_id,
                AssignmentStatusRow.student_id == student_id,
                AssignmentStatusRow.status != AssignmentStatus.COMPLETED,
            )
        )
        return list((await self.session.execute(stmt)).all())


class AssignmentStatusRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, row: AssignmentStatusRow) -> AssignmentStatusRow:
        self.session.add(row)
        await self.session.flush()
        return row

    async def list_for_assignment(self, assignment_id: uuid.UUID) -> list[AssignmentStatusRow]:
        stmt = select(AssignmentStatusRow).where(AssignmentStatusRow.assignment_id == assignment_id)
        return list((await self.session.execute(stmt)).scalars().all())
