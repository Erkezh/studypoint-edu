from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, question_id: int) -> Question | None:
        return await self.session.get(Question, question_id)

    async def list_for_skill_levels(self, *, skill_id: int, levels: list[int], exclude_ids: list[int], limit: int) -> list[Question]:
        stmt = (
            select(Question)
            .where(Question.skill_id == skill_id, Question.level.in_(levels))
            .order_by(func.random())
            .limit(limit)
        )
        if exclude_ids:
            stmt = stmt.where(~Question.id.in_(exclude_ids))
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_admin(self, *, skill_id: int | None, page: int, page_size: int) -> tuple[list[Question], int]:
        stmt = select(Question)
        count_stmt = select(func.count()).select_from(Question)
        if skill_id is not None:
            stmt = stmt.where(Question.skill_id == skill_id)
            count_stmt = count_stmt.where(Question.skill_id == skill_id)
        total = int((await self.session.execute(count_stmt)).scalar_one())
        stmt = stmt.order_by(Question.id).offset((page - 1) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, total

    async def create(self, **kwargs) -> Question:
        q = Question(**kwargs)
        self.session.add(q)
        await self.session.flush()
        return q
