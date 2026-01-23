from __future__ import annotations

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.catalog import Grade, Skill, Subject
from app.models.question import Question
from app.schemas.admin import (
    BulkImportRequest,
    BulkImportResponse,
    GradeCreate,
    GradeUpdate,
    QuestionCreate,
    QuestionUpdate,
    SkillCreate,
    SkillUpdate,
    SubjectCreate,
    SubjectUpdate,
)


class AdminService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def list_subjects(self) -> list[Subject]:
        return list((await self.session.execute(select(Subject).order_by(Subject.id))).scalars().all())

    async def create_subject(self, req: SubjectCreate) -> Subject:
        subject = Subject(slug=req.slug, title=req.title)
        self.session.add(subject)
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Subject slug already exists") from e
        return subject

    async def update_subject(self, subject_id: int, req: SubjectUpdate) -> Subject:
        subject = await self.session.get(Subject, subject_id)
        if subject is None:
            raise AppError(status_code=404, code="not_found", message="Subject not found")
        if req.slug is not None:
            subject.slug = req.slug
        if req.title is not None:
            subject.title = req.title
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Subject slug already exists") from e
        return subject

    async def delete_subject(self, subject_id: int) -> None:
        subject = await self.session.get(Subject, subject_id)
        if subject is None:
            return
        await self.session.delete(subject)

    async def list_grades(self) -> list[Grade]:
        return list((await self.session.execute(select(Grade).order_by(Grade.number))).scalars().all())

    async def create_grade(self, req: GradeCreate) -> Grade:
        grade = Grade(number=req.number, title=req.title)
        self.session.add(grade)
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Grade number already exists") from e
        return grade

    async def update_grade(self, grade_id: int, req: GradeUpdate) -> Grade:
        grade = await self.session.get(Grade, grade_id)
        if grade is None:
            raise AppError(status_code=404, code="not_found", message="Grade not found")
        if req.number is not None:
            grade.number = req.number
        if req.title is not None:
            grade.title = req.title
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Grade number already exists") from e
        return grade

    async def delete_grade(self, grade_id: int) -> None:
        grade = await self.session.get(Grade, grade_id)
        if grade is None:
            return
        await self.session.delete(grade)

    async def list_skills(self, *, page: int, page_size: int) -> tuple[list[Skill], int]:
        from sqlalchemy import func

        total = int((await self.session.execute(select(func.count()).select_from(Skill))).scalar_one())
        stmt = select(Skill).order_by(Skill.id).offset((page - 1) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, total

    async def create_skill(self, req: SkillCreate) -> Skill:
        # Извлекаем generator_code и generator_metadata отдельно, так как они не в базовой модели
        skill_data = req.model_dump(exclude={'generator_code', 'generator_metadata'})
        skill = Skill(**skill_data)
        
        # Устанавливаем generator_code и generator_metadata если они есть
        if hasattr(req, 'generator_code') and req.generator_code:
            skill.generator_code = req.generator_code
        if hasattr(req, 'generator_metadata') and req.generator_metadata:
            skill.generator_metadata = req.generator_metadata
        
        self.session.add(skill)
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Skill code already exists for this subject+grade") from e
        return skill

    async def update_skill(self, skill_id: int, req: SkillUpdate) -> Skill:
        skill = await self.session.get(Skill, skill_id)
        if skill is None:
            raise AppError(status_code=404, code="not_found", message="Skill not found")
        for field, value in req.model_dump(exclude_unset=True).items():
            setattr(skill, field, value)
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Skill code already exists for this subject+grade") from e
        return skill

    async def delete_skill(self, skill_id: int) -> None:
        skill = await self.session.get(Skill, skill_id)
        if skill is None:
            return
        await self.session.delete(skill)

    async def list_questions(self, *, page: int, page_size: int, skill_id: int | None) -> tuple[list[Question], int]:
        from sqlalchemy import func

        stmt = select(Question)
        count_stmt = select(func.count()).select_from(Question)
        if skill_id is not None:
            stmt = stmt.where(Question.skill_id == skill_id)
            count_stmt = count_stmt.where(Question.skill_id == skill_id)
        total = int((await self.session.execute(count_stmt)).scalar_one())
        stmt = stmt.order_by(Question.id).offset((page - 1) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, total

    async def create_question(self, req: QuestionCreate) -> Question:
        from sqlalchemy.exc import IntegrityError
        
        q = Question(**req.model_dump())
        self.session.add(q)
        try:
            await self.session.flush()
        except IntegrityError as e:
            # Проверяем, что это ошибка foreign key
            if "foreign key constraint" in str(e.orig).lower() or "ForeignKeyViolationError" in str(type(e.orig)):
                if "skill_id" in str(e.orig):
                    from app.core.errors import AppError
                    raise AppError(
                        status_code=404,
                        code="skill_not_found",
                        message=f"Skill with id {req.skill_id} not found",
                        details="The specified skill_id does not exist in the database"
                    )
            raise
        return q

    async def update_question(self, question_id: int, req: QuestionUpdate) -> Question:
        q = await self.session.get(Question, question_id)
        if q is None:
            raise AppError(status_code=404, code="not_found", message="Question not found")
        for field, value in req.model_dump(exclude_unset=True).items():
            setattr(q, field, value)
        await self.session.flush()
        return q

    async def delete_question(self, question_id: int) -> None:
        q = await self.session.get(Question, question_id)
        if q is None:
            return
        await self.session.delete(q)

    async def bulk_import(self, req: BulkImportRequest) -> BulkImportResponse:
        skills_created = 0
        questions_created = 0
        for s in req.skills:
            skill = Skill(**s.model_dump())
            self.session.add(skill)
            try:
                await self.session.flush()
                skills_created += 1
            except IntegrityError:
                raise AppError(status_code=409, code="conflict", message="Skill conflict during import")

        for q in req.questions:
            question = Question(**q.model_dump())
            self.session.add(question)
            await self.session.flush()
            questions_created += 1
        return BulkImportResponse(skills_created=skills_created, questions_created=questions_created)
