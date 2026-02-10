from __future__ import annotations

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.catalog import Grade, Skill, Subject
from app.models.topic import Topic
from app.models.question import Question
from app.models.enums import QuestionType
from app.repositories.plugin_repo import PluginRepository
from app.schemas.admin import (
    AddPluginToTestRequest,
    BulkImportRequest,
    BulkImportResponse,
    GradeCreate,
    GradeUpdate,
    PluginQuestionCreate,
    QuestionCreate,
    QuestionUpdate,
    SkillCreate,
    SkillUpdate,
    SubjectCreate,
    SubjectUpdate,
    TopicCreate,
    TopicUpdate,
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

    # --- Topic CRUD ---

    async def list_topics(self, *, page: int, page_size: int) -> tuple[list[Topic], int]:
        from sqlalchemy import func

        total = int((await self.session.execute(select(func.count()).select_from(Topic))).scalar_one())
        stmt = select(Topic).order_by(Topic.order, Topic.id).offset((page - 1) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        return items, total

    async def create_topic(self, req: TopicCreate) -> Topic:
        topic = Topic(
            slug=req.slug,
            title=req.title,
            description=req.description,
            icon=req.icon,
            order=req.order,
            is_published=req.is_published,
        )
        self.session.add(topic)
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Topic slug already exists") from e
        return topic

    async def update_topic(self, topic_id: int, req: TopicUpdate) -> Topic:
        topic = await self.session.get(Topic, topic_id)
        if topic is None:
            raise AppError(status_code=404, code="not_found", message="Topic not found")
        if req.slug is not None:
            topic.slug = req.slug
        if req.title is not None:
            topic.title = req.title
        if req.description is not None:
            topic.description = req.description
        if req.icon is not None:
            topic.icon = req.icon
        if req.order is not None:
            topic.order = req.order
        if req.is_published is not None:
            topic.is_published = req.is_published
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Topic slug already exists") from e
        return topic

    async def delete_topic(self, topic_id: int) -> None:
        topic = await self.session.get(Topic, topic_id)
        if topic is None:
            return
        await self.session.delete(topic)

    # --- Skill CRUD ---

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
        from sqlalchemy import delete
        
        skill = await self.session.get(Skill, skill_id)
        if skill is None:
            raise AppError(status_code=404, code="not_found", message="Skill not found")
        
        # Сначала удаляем все связанные вопросы (каскадное удаление может не сработать из-за ограничений БД)
        # Используем массовое удаление для эффективности
        await self.session.execute(delete(Question).where(Question.skill_id == skill_id))
        await self.session.flush()  # Важно: flush() сохраняет изменения в БД
        
        # Затем удаляем сам навык
        await self.session.delete(skill)
        await self.session.flush()  # Важно: flush() сохраняет изменения в БД
        # Транзакция коммитится автоматически через session.begin() в get_db_session()

    async def list_questions(
        self, 
        *, 
        page: int, 
        page_size: int, 
        skill_id: int | None,
        search: str | None = None,
        sort_order: str = "desc"
    ) -> tuple[list[Question], int, dict[int, str]]:
        from sqlalchemy import func
        from app.models.catalog import Skill

        stmt = select(Question)
        count_stmt = select(func.count()).select_from(Question)
        
        # Фильтр по skill_id
        if skill_id is not None:
            stmt = stmt.where(Question.skill_id == skill_id)
            count_stmt = count_stmt.where(Question.skill_id == skill_id)
        
        # Поиск по названию навыка
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.join(Skill, Question.skill_id == Skill.id).where(Skill.title.ilike(search_pattern))
            count_stmt = count_stmt.join(Skill, Question.skill_id == Skill.id).where(Skill.title.ilike(search_pattern))
        
        total = int((await self.session.execute(count_stmt)).scalar_one())
        
        # Сортировка по дате создания
        if sort_order == "asc":
            stmt = stmt.order_by(Question.created_at.asc(), Question.id.asc())
        else:
            stmt = stmt.order_by(Question.created_at.desc(), Question.id.desc())
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        
        # Получаем названия навыков
        skill_ids = list(set(q.skill_id for q in items))
        skill_names: dict[int, str] = {}
        if skill_ids:
            skills_stmt = select(Skill.id, Skill.title).where(Skill.id.in_(skill_ids))
            skills_result = await self.session.execute(skills_stmt)
            skill_names = {row[0]: row[1] for row in skills_result.all()}
        
        return items, total, skill_names

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

    async def create_plugin_question(self, req: PluginQuestionCreate) -> Question:
        """Добавить плагин в тест (навык). Создаёт вопрос типа PLUGIN."""
        repo = PluginRepository(self.session)
        if req.plugin_version:
            plugin = await repo.get_by_plugin_id_and_version(req.plugin_id, req.plugin_version)
        else:
            plugin = await repo.get_by_plugin_id(req.plugin_id)
        if plugin is None:
            raise AppError(
                status_code=404,
                code="plugin_not_found",
                message=f"Плагин {req.plugin_id}" + (f"@{req.plugin_version}" if req.plugin_version else "") + " не найден",
            )
        if not plugin.is_published:
            raise AppError(
                status_code=400,
                code="plugin_not_published",
                message="В тест можно добавить только опубликованный плагин. Сначала опубликуйте его.",
            )
        create = QuestionCreate(
            skill_id=req.skill_id,
            type=QuestionType.PLUGIN,
            prompt=plugin.name,
            data={
                "plugin_id": plugin.plugin_id,
                "plugin_version": plugin.version,
                "entry": plugin.entry,
                "height": plugin.height,
            },
            correct_answer={},
            explanation="",
            level=1,
        )
        return await self.create_question(create)

    async def add_plugin_to_test(self, req: AddPluginToTestRequest) -> dict:
        """Создать навык из плагина и добавить в тест. Плагин сам становится навыком."""
        import re

        grade = await self.session.get(Grade, req.grade_id)
        if grade is None:
            raise AppError(status_code=404, code="grade_not_found", message="Класс не найден")

        repo = PluginRepository(self.session)
        if req.plugin_version:
            plugin = await repo.get_by_plugin_id_and_version(req.plugin_id, req.plugin_version)
        else:
            plugin = await repo.get_by_plugin_id(req.plugin_id)
        if plugin is None:
            raise AppError(
                status_code=404,
                code="plugin_not_found",
                message=f"Плагин {req.plugin_id}" + (f"@{req.plugin_version}" if req.plugin_version else "") + " не найден",
            )
        if not plugin.is_published:
            raise AppError(
                status_code=400,
                code="plugin_not_published",
                message="В тест можно добавить только опубликованный плагин. Сначала опубликуйте его.",
            )

        subjects = await self.list_subjects()
        subject_id = subjects[0].id if subjects else 1

        # Проверяем, не был ли уже этот плагин добавлен в тест для данного класса
        # Ищем вопрос PLUGIN с таким plugin_id в навыках этого класса
        from sqlalchemy import and_
        
        # Сначала находим все навыки для этого класса
        skills_stmt = select(Skill).where(
            Skill.subject_id == subject_id,
            Skill.grade_id == req.grade_id
        )
        skills_result = await self.session.execute(skills_stmt)
        skills = skills_result.scalars().all()
        
        if skills:
            skill_ids = [s.id for s in skills]
            # Ищем вопросы PLUGIN для этих навыков
            questions_stmt = select(Question).where(
                Question.type == QuestionType.PLUGIN,
                Question.skill_id.in_(skill_ids)
            )
            questions_result = await self.session.execute(questions_stmt)
            questions = questions_result.scalars().all()
            
            # Проверяем, есть ли вопрос с таким plugin_id
            for question in questions:
                question_data = question.data or {}
                if question_data.get('plugin_id') == plugin.plugin_id:
                    # Находим навык для этого вопроса
                    skill = await self.session.get(Skill, question.skill_id)
                    if skill:
                        # Возвращаем информацию о существующем навыке
                        # Это не ошибка, просто плагин уже добавлен
                        return {
                            "skill_id": skill.id,
                            "skill_title": skill.title,
                            "question_id": question.id,
                            "already_exists": True,
                            "message": f"Плагин уже добавлен в тест как навык «{skill.title}»"
                        }

        base = re.sub(r"[^a-zA-Z0-9_-]", "", plugin.plugin_id)[:16] or "plugin"
        code = base
        suffix = 0
        exists_stmt = select(Skill).where(
            Skill.subject_id == subject_id,
            Skill.grade_id == req.grade_id,
            Skill.code == code,
        )
        while (await self.session.execute(exists_stmt)).scalar_one_or_none() is not None:
            suffix += 1
            if suffix > 99:
                # Если не удалось подобрать код, возможно плагин уже добавлен
                # Проверяем еще раз более тщательно
                all_skills_stmt = select(Skill).where(
                    Skill.subject_id == subject_id,
                    Skill.grade_id == req.grade_id
                )
                all_skills = (await self.session.execute(all_skills_stmt)).scalars().all()
                for skill in all_skills:
                    skill_questions_stmt = select(Question).where(
                        Question.skill_id == skill.id,
                        Question.type == QuestionType.PLUGIN
                    )
                    skill_questions = (await self.session.execute(skill_questions_stmt)).scalars().all()
                    for q in skill_questions:
                        if (q.data or {}).get('plugin_id') == plugin.plugin_id:
                            return {
                                "skill_id": skill.id,
                                "skill_title": skill.title,
                                "question_id": q.id,
                                "already_exists": True,
                                "message": f"Плагин уже добавлен в тест как навык «{skill.title}»"
                            }
                raise AppError(
                    status_code=409, 
                    code="conflict", 
                    message=f"Не удалось подобрать уникальный код навыка для плагина {plugin.plugin_id}. Возможно, слишком много навыков с похожими кодами."
                )
            code = f"{base}_{suffix}"[:16]
            exists_stmt = select(Skill).where(
                Skill.subject_id == subject_id,
                Skill.grade_id == req.grade_id,
                Skill.code == code,
            )

        skill_req = SkillCreate(
            subject_id=subject_id,
            grade_id=req.grade_id,
            topic_id=req.topic_id,
            code=code,
            title=plugin.name,
            description="",
            tags=[],
            difficulty=1,
        )
        
        try:
            skill = await self.create_skill(skill_req)
        except AppError as e:
            if e.code == "conflict":
                # Если все же возник конфликт, пробуем найти существующий навык
                existing_skill_stmt = select(Skill).where(
                    Skill.subject_id == subject_id,
                    Skill.grade_id == req.grade_id,
                    Skill.title == plugin.name
                )
                existing_skill = (await self.session.execute(existing_skill_stmt)).scalar_one_or_none()
                if existing_skill:
                    # Проверяем, есть ли уже вопрос PLUGIN для этого навыка
                    existing_q_stmt = select(Question).where(
                        Question.skill_id == existing_skill.id,
                        Question.type == QuestionType.PLUGIN
                    )
                    existing_qs = (await self.session.execute(existing_q_stmt)).scalars().all()
                    for existing_q in existing_qs:
                        question_data = existing_q.data or {}
                        if question_data.get('plugin_id') == plugin.plugin_id:
                            return {
                                "skill_id": existing_skill.id,
                                "skill_title": existing_skill.title,
                                "question_id": existing_q.id,
                                "already_exists": True
                            }
            raise

        q = await self.create_plugin_question(
            PluginQuestionCreate(skill_id=skill.id, plugin_id=plugin.plugin_id, plugin_version=plugin.version)
        )
        return {"skill_id": skill.id, "skill_title": skill.title, "question_id": q.id}

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
            raise AppError(status_code=404, code="not_found", message="Question not found")
        await self.session.delete(q)
        await self.session.flush()

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
