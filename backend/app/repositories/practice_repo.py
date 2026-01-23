from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.practice import PracticeAttempt, PracticeSession, ProgressSnapshot


class PracticeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(self, session_obj: PracticeSession) -> PracticeSession:
        self.session.add(session_obj)
        await self.session.flush()
        return session_obj

    async def get_session(self, *, session_id: str) -> PracticeSession | None:
        try:
            sid = uuid.UUID(session_id)
        except ValueError:
            return None
        return await self.session.get(PracticeSession, sid)

    async def get_active_session(self, *, user_id: uuid.UUID, skill_id: int) -> PracticeSession | None:
        stmt = (
            select(PracticeSession)
            .where(PracticeSession.user_id == user_id, PracticeSession.skill_id == skill_id, PracticeSession.finished_at.is_(None))
            .order_by(PracticeSession.last_activity_at.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def has_attempt(self, *, session_id: uuid.UUID, question_id: int) -> bool:
        stmt = select(func.count()).select_from(PracticeAttempt).where(
            PracticeAttempt.session_id == session_id, PracticeAttempt.question_id == question_id
        )
        return int((await self.session.execute(stmt)).scalar_one()) > 0

    async def add_attempt(self, attempt: PracticeAttempt) -> PracticeAttempt:
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def get_snapshot(self, *, user_id: uuid.UUID, skill_id: int) -> ProgressSnapshot | None:
        return await self.session.get(ProgressSnapshot, {"user_id": user_id, "skill_id": skill_id})

    async def upsert_snapshot(self, snap: ProgressSnapshot) -> ProgressSnapshot:
        self.session.add(snap)
        await self.session.flush()
        return snap
