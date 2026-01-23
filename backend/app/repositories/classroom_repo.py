from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.classroom import Classroom, Enrollment


class ClassroomRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, classroom: Classroom) -> Classroom:
        self.session.add(classroom)
        await self.session.flush()
        return classroom

    async def list_for_teacher(self, teacher_id: uuid.UUID) -> list[Classroom]:
        stmt = select(Classroom).where(Classroom.teacher_id == teacher_id).order_by(Classroom.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def get(self, classroom_id: str) -> Classroom | None:
        try:
            cid = uuid.UUID(classroom_id)
        except ValueError:
            return None
        return await self.session.get(Classroom, cid)

    async def enroll(self, enrollment: Enrollment) -> Enrollment:
        self.session.add(enrollment)
        await self.session.flush()
        return enrollment

    async def list_enrollments(self, classroom_id: uuid.UUID) -> list[Enrollment]:
        stmt = select(Enrollment).where(Enrollment.classroom_id == classroom_id).order_by(Enrollment.enrolled_at.asc())
        return list((await self.session.execute(stmt)).scalars().all())
