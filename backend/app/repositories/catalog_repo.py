from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Grade, Skill, Subject


class SubjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[Subject]:
        return list((await self.session.execute(select(Subject).order_by(Subject.id))).scalars().all())

    async def get(self, subject_id: int) -> Subject | None:
        return await self.session.get(Subject, subject_id)

    async def get_by_slug(self, slug: str) -> Subject | None:
        return (await self.session.execute(select(Subject).where(Subject.slug == slug))).scalar_one_or_none()

    async def create(self, *, slug: str, title: str) -> Subject:
        subject = Subject(slug=slug, title=title)
        self.session.add(subject)
        await self.session.flush()
        return subject


class GradeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[Grade]:
        return list((await self.session.execute(select(Grade).order_by(Grade.number))).scalars().all())

    async def get_by_number(self, number: int) -> Grade | None:
        return (await self.session.execute(select(Grade).where(Grade.number == number))).scalar_one_or_none()

    async def get(self, grade_id: int) -> Grade | None:
        return await self.session.get(Grade, grade_id)

    async def create(self, *, number: int, title: str) -> Grade:
        grade = Grade(number=number, title=title)
        self.session.add(grade)
        await self.session.flush()
        return grade


class SkillRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        *,
        subject_id: int | None,
        grade_id: int | None,
        query: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Skill], int]:
        stmt = select(Skill).where(Skill.is_published.is_(True))
        count_stmt = select(func.count()).select_from(Skill).where(Skill.is_published.is_(True))

        if subject_id is not None:
            stmt = stmt.where(Skill.subject_id == subject_id)
            count_stmt = count_stmt.where(Skill.subject_id == subject_id)
        if grade_id is not None:
            stmt = stmt.where(Skill.grade_id == grade_id)
            count_stmt = count_stmt.where(Skill.grade_id == grade_id)
        if query:
            q = f"%{query.strip()}%"
            stmt = stmt.where((Skill.title.ilike(q)) | (Skill.code.ilike(q)))
            count_stmt = count_stmt.where((Skill.title.ilike(q)) | (Skill.code.ilike(q)))

        total = (await self.session.execute(count_stmt)).scalar_one()
        stmt = stmt.order_by(Skill.grade_id, Skill.subject_id, Skill.code).offset((page - 1) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, int(total)

    async def get(self, skill_id: int) -> Skill | None:
        return await self.session.get(Skill, skill_id)

    async def create(self, **kwargs) -> Skill:
        skill = Skill(**kwargs)
        self.session.add(skill)
        await self.session.flush()
        return skill

