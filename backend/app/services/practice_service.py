from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.enums import MistakeType, PracticeZone, QuestionType, SubscriptionPlan
from app.models.practice import PracticeAttempt, PracticeSession, ProgressSnapshot
from app.models.profile import StudentProfile
from app.models.enums import AssignmentStatus
from app.repositories.assignment_repo import AssignmentRepository
from app.repositories.catalog_repo import SkillRepository
from app.repositories.practice_repo import PracticeRepository
from app.repositories.question_repo import QuestionRepository
from app.repositories.subscription_repo import SubscriptionRepository
from app.schemas.practice import PracticeSessionResponse, PracticeSubmitRequest, PracticeSubmitResponse, QuestionPublic
from app.services.generator_service import GeneratorService
from app.services.scoring import WindowStats, compute_next_smartscore, zone_for_score
from app.services.timer_service import apply_active_time_delta, inactivity_threshold_seconds_for_grade
from app.utils.redis import get_redis
from app.utils.time import utc_now


class PracticeService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.skills = SkillRepository(session)
        self.questions = QuestionRepository(session)
        self.practice = PracticeRepository(session)
        self.subscriptions = SubscriptionRepository(session)
        self.assignments = AssignmentRepository(session)

    async def start_session(self, *, user_id, skill_id: int) -> PracticeSessionResponse:
        import logging
        logger = logging.getLogger(__name__)
        
        user_uuid = _parse_uuid(user_id)
        skill = await self.skills.get(skill_id)
        if skill is None or not skill.is_published:
            raise AppError(status_code=404, code="not_found", message="Skill not found")
        
        logger.info(f"Starting session for skill {skill_id}, has_generator: {bool(skill.generator_code)}")

        # Resume unfinished session if not expired (IXL-like).
        active = await self.practice.get_active_session(user_id=user_uuid, skill_id=skill_id)
        if active is not None:
            if _is_expired(active.last_activity_at):
                active.finished_at = utc_now()
                await self.session.flush()
            else:
                q = None
                if active.last_question_id is not None:
                    q = await self.questions.get(active.last_question_id)
                return await self._to_session_response(active, current_question=q)

        grade_level = (
            await self.session.execute(select(StudentProfile.grade_level).where(StudentProfile.user_id == user_uuid))
        ).scalar_one_or_none()
        threshold = inactivity_threshold_seconds_for_grade(int(grade_level) if grade_level is not None else None)

        session_state: dict[str, Any] = {
            "recent_question_ids": [],
            "recent_window": {"correct": 0, "total": 0},
            "entered_challenge_zone_at": None,
            "wrong_streak": 0,  # Серия неправильных ответов подряд
        }

        now = utc_now()
        ps = PracticeSession(
            user_id=user_uuid,
            skill_id=skill_id,
            started_at=now,
            finished_at=None,
            questions_answered=0,
            correct_count=0,
            wrong_count=0,
            smartscore=0,
            time_elapsed_sec=0,
            current_smartscore=0,
            best_smartscore=0,
            total_questions_answered=0,
            total_correct=0,
            total_incorrect=0,
            current_streak_correct=0,
            max_streak_correct=0,
            current_zone=PracticeZone.LEARNING,
            last_question_id=None,
            last_activity_at=now,
            active_time_seconds=0,
            inactivity_threshold_seconds=threshold,
            state=session_state,
        )

        await self.practice.create_session(ps)
        
        # Если навык использует генератор, генерируем вопрос
        q = None
        if skill.generator_code:
            try:
                q_data = GeneratorService.execute_generator(
                    skill.generator_code,
                    skill.generator_metadata or {}
                )
                # Сохраняем сгенерированный вопрос в state сессии
                # Убеждаемся, что generated_questions существует
                if 'generated_questions' not in ps.state:
                    ps.state['generated_questions'] = {}
                # Используем длину словаря для генерации ID
                question_id = f"generated_{len(ps.state['generated_questions'])}"
                ps.state['generated_questions'][question_id] = q_data
                ps.state["current_question_id"] = question_id
                ps.last_question_id = None  # Для генераторов не используем question_id из БД
                # Сохраняем изменения в state
                await self.session.flush()
                q = _generated_to_question_public(q_data, question_id)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error executing generator for skill {skill_id}: {e}", exc_info=True)
                # Если генератор не работает, пытаемся использовать вопросы из БД
                try:
                    q = await self._select_next_question(ps)
                    ps.last_question_id = q.id
                    ps.state["current_question_id"] = q.id
                    ps.state["recent_question_ids"] = _push_recent(ps.state.get("recent_question_ids", []), q.id)
                except AppError as db_error:
                    logger.error(f"Error getting question from DB for skill {skill_id}: {db_error}", exc_info=True)
                    # Если и из БД не получилось, возвращаем понятную ошибку
                    if db_error.status_code == 404 and db_error.code == "not_found":
                        raise AppError(
                            status_code=400,
                            code="no_questions_available",
                            message=f"Skill {skill_id} has a generator with errors and no questions in DB. Please fix the generator code or add questions to this skill. Generator error: {str(e)}"
                        )
                    raise AppError(
                        status_code=500,
                        code="generator_error",
                        message=f"Failed to generate question: {str(e)}. Also failed to get question from DB: {str(db_error)}"
                    )
                except Exception as db_error:
                    logger.error(f"Unexpected error getting question from DB for skill {skill_id}: {db_error}", exc_info=True)
                    raise AppError(
                        status_code=500,
                        code="generator_error",
                        message=f"Failed to generate question: {str(e)}. Also failed to get question from DB: {str(db_error)}"
                    )
        else:
            # Старый способ - получаем вопрос из БД
            try:
                q = await self._select_next_question(ps)
                ps.last_question_id = q.id
                ps.state["current_question_id"] = q.id
                ps.state["recent_question_ids"] = _push_recent(ps.state.get("recent_question_ids", []), q.id)
            except AppError as e:
                if e.status_code == 404 and e.code == "not_found":
                    # Если нет вопросов в БД, это ошибка конфигурации навыка
                    raise AppError(
                        status_code=400,
                        code="no_questions_available",
                        message=f"Skill {skill_id} has no questions and no generator. Please add questions or a generator to this skill."
                    )
                raise
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Unexpected error selecting question for skill {skill_id}: {e}", exc_info=True)
                raise AppError(
                    status_code=500,
                    code="question_selection_error",
                    message=f"Failed to select question for skill {skill_id}: {str(e)}"
                )
        
        # Проверяем, что вопрос был создан
        if q is None:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"No question created for skill {skill_id}, has_generator: {bool(skill.generator_code)}")
            raise AppError(
                status_code=500,
                code="no_question_created",
                message=f"Failed to create question for skill {skill_id}. Please check skill configuration."
            )
        
        await self.session.flush()

        return await self._to_session_response(ps, current_question=q)

    async def get_session(self, *, user_id, session_id: str) -> PracticeSessionResponse:
        user_uuid = _parse_uuid(user_id)
        ps = await self.practice.get_session(session_id=session_id)
        if ps is None or ps.user_id != user_uuid:
            raise AppError(status_code=404, code="not_found", message="Session not found")
        
        skill = await self.skills.get(ps.skill_id)
        q = None
        
        # Если навык использует генератор, получаем вопрос из state
        if skill and skill.generator_code:
            current_q_id = ps.state.get("current_question_id")
            if current_q_id:
                generated_questions = ps.state.get("generated_questions", {})
                if current_q_id in generated_questions:
                    q_data = generated_questions[current_q_id]
                    q = _generated_to_question_public(q_data, current_q_id)
        elif ps.last_question_id is not None:
            # Старый способ - получаем вопрос из БД
            q = await self.questions.get(ps.last_question_id)
        
        return await self._to_session_response(ps, current_question=q)

    async def next_question(self, *, user_id, session_id: str) -> dict:
        user_uuid = _parse_uuid(user_id)
        ps = await self.practice.get_session(session_id=session_id)
        if ps is None or ps.user_id != user_uuid:
            raise AppError(status_code=404, code="not_found", message="Session not found")
        if ps.finished_at is not None:
            return {"finished": True, "question": None}

        await self._touch_activity(ps)

        skill = await self.skills.get(ps.skill_id)
        
        # Если навык использует генератор, генерируем новый вопрос
        if skill and skill.generator_code:
            q_data = GeneratorService.execute_generator(
                skill.generator_code,
                skill.generator_metadata or {}
            )
            # Убеждаемся, что generated_questions существует
            if 'generated_questions' not in ps.state:
                ps.state['generated_questions'] = {}
            # Используем длину словаря для генерации ID
            question_id = f"generated_{len(ps.state['generated_questions'])}"
            ps.state['generated_questions'][question_id] = q_data
            ps.state["current_question_id"] = question_id
            ps.last_question_id = None
            # Сохраняем изменения в state
            await self.session.flush()
            q = _generated_to_question_public(q_data, question_id)
        else:
            # Старый способ - получаем вопрос из БД
            if ps.last_question_id is not None:
                already = await self.practice.has_attempt(session_id=ps.id, question_id=ps.last_question_id)
                if not already:
                    q = await self.questions.get(ps.last_question_id)
                    if q is not None:
                        return {"finished": False, "question": _to_question_public(q).model_dump(mode="json")}

            q = await self._select_next_question(ps)
            ps.last_question_id = q.id
            ps.state["current_question_id"] = q.id
            ps.state["recent_question_ids"] = _push_recent(ps.state.get("recent_question_ids", []), q.id)
        
        await self.session.flush()

        return {"finished": False, "question": q.model_dump(mode="json")}

    async def submit(self, *, user_id, session_id: str, req: PracticeSubmitRequest) -> PracticeSubmitResponse:
        import logging
        logger = logging.getLogger(__name__)
        
        user_uuid = _parse_uuid(user_id)
        ps = await self.practice.get_session(session_id=session_id)
        if ps is None or ps.user_id != user_uuid:
            raise AppError(status_code=404, code="not_found", message="Session not found")
        
        # Проверяем состояние сессии перед обработкой
        logger.info(
            f"Submitting answer for session {session_id}: "
            f"finished_at={ps.finished_at}, "
            f"questions_answered={ps.total_questions_answered}, "
            f"smartscore={ps.current_smartscore}, "
            f"wrong_streak={ps.state.get('wrong_streak', 0)}"
        )
        
        if ps.finished_at is not None:
            logger.warning(
                f"Session {session_id} already finished: "
                f"finished_at={ps.finished_at}, "
                f"questions_answered={ps.total_questions_answered}, "
                f"smartscore={ps.current_smartscore}, "
                f"wrong_streak={ps.state.get('wrong_streak', 0)}"
            )
            raise AppError(status_code=409, code="conflict", message="Session already finished")

        await self._enforce_subscription_limit(user_id=user_uuid)
        await self._touch_activity(ps)

        skill = await self.skills.get(ps.skill_id)
        is_generator_skill = skill and skill.generator_code
        
        if is_generator_skill:
            # Для генераторов проверяем current_question_id из state
            current_q_id = ps.state.get("current_question_id")
            generated_questions = ps.state.get("generated_questions", {})
            
            import logging
            logger = logging.getLogger(__name__)
            
            # Проверяем, что current_q_id не None
            if current_q_id is None:
                logger.error(f"current_question_id is None in session state. State: {ps.state}")
                raise AppError(status_code=404, code="not_found", message="Current question ID is not set in session")
            
            logger.info(
                f"Generator skill submit check: "
                f"current_q_id={current_q_id} (type: {type(current_q_id)}), "
                f"req.question_id={req.question_id} (type: {type(req.question_id)}), "
                f"generated_questions_keys={list(generated_questions.keys())}, "
                f"key_types={[type(k) for k in generated_questions.keys()]}, "
                f"current_q_id == str(req.question_id): {current_q_id == str(req.question_id)}, "
                f"current_q_id in generated_questions: {current_q_id in generated_questions}, "
                f"state_keys={list(ps.state.keys())}"
            )
            
            if current_q_id != str(req.question_id):
                logger.error(f"Question ID mismatch: current_q_id={current_q_id}, req.question_id={req.question_id}")
                raise AppError(status_code=409, code="conflict", message="Question does not match current session state")
            
            logger.info(f"Checking if {current_q_id} is in generated_questions: {current_q_id in generated_questions}")
            if current_q_id not in generated_questions:
                logger.error(
                    f"Generated question not found: "
                    f"current_q_id={current_q_id} (type: {type(current_q_id)}), "
                    f"available_keys={list(generated_questions.keys())}, "
                    f"key_types={[type(k) for k in generated_questions.keys()]}, "
                    f"current_q_id in generated_questions: {current_q_id in generated_questions}, "
                    f"state={ps.state}"
                )
                raise AppError(status_code=404, code="not_found", message="Generated question not found in session")
            
            logger.info(f"Found generated question: {current_q_id}, proceeding with validation")
            q_data = generated_questions[current_q_id]
            question_type = QuestionType(q_data.get('type', 'MCQ'))
            question_data = q_data.get('data', {})
            
            # Проверяем, что вопрос еще не был отвечен
            answered_questions = ps.state.get("answered_question_ids", [])
            if current_q_id in answered_questions:
                raise AppError(status_code=409, code="conflict", message="Question already answered in this session")
            
            logger.info(f"Validating submitted answer for question {current_q_id}")
            _validate_submitted_answer(question_type, question_data, req.submitted_answer)
            
            # Проверяем ответ используя генератор
            logger.info(f"Calling GeneratorService.validate_answer for question {current_q_id}")
            is_correct, explanation = await GeneratorService.validate_answer(
                skill.generator_code,
                q_data,
                req.submitted_answer,
                skill.generator_metadata or {}
            )
            logger.info(f"GeneratorService.validate_answer returned: is_correct={is_correct}, explanation={explanation}")
            
            # Сохраняем, что вопрос был отвечен
            logger.info(f"Marking question {current_q_id} as answered")
            ps.state.setdefault("answered_question_ids", []).append(current_q_id)
            question_level = q_data.get('level', 1)
            question = None  # Для генераторов question = None
            # Для генераторов правильный ответ уже в q_data
            correct_answer = q_data.get('correct_answer', {})
            explanation = q_data.get('explanation')
            logger.info(f"Extracted question data: level={question_level}, correct_answer={correct_answer}, explanation={explanation}")
            # Для генераторов is_correct уже определен через GeneratorService.validate_answer
            # Не нужно вызывать _is_correct() для генераторов
            question_type = QuestionType(q_data.get('type', 'MCQ'))
            question_data = q_data.get('data', {})
            # is_correct уже определен выше через GeneratorService.validate_answer
            # Для генераторов is_correct уже определен через GeneratorService.validate_answer
            # Не нужно вызывать _is_correct() для генераторов
            question_type = QuestionType(q_data.get('type', 'MCQ'))
            question_data = q_data.get('data', {})
        else:
            # Старый способ - получаем вопрос из БД
            # Сравниваем с учетом типов (может быть int или str)
            if ps.last_question_id is not None:
                # Приводим к одному типу для сравнения
                last_q_id = str(ps.last_question_id) if ps.last_question_id is not None else None
                req_q_id = str(req.question_id) if req.question_id is not None else None
                
                if last_q_id != req_q_id:
                    logger.warning(
                        f"Question ID mismatch: last_question_id={ps.last_question_id} (type: {type(ps.last_question_id)}), "
                        f"req.question_id={req.question_id} (type: {type(req.question_id)}), "
                        f"session_id={session_id}"
                    )
                    raise AppError(status_code=409, code="conflict", message="Question does not match current session state")

            question = await self.questions.get(req.question_id)
            if question is None or question.skill_id != ps.skill_id:
                raise AppError(status_code=404, code="not_found", message="Question not found")

            if await self.practice.has_attempt(session_id=ps.id, question_id=question.id):
                raise AppError(status_code=409, code="conflict", message="Question already answered in this session")

            _validate_submitted_answer(question.type, question.data, req.submitted_answer)
            question_type = question.type
            question_data = question.data
            question_level = question.level
            explanation = question.explanation

            if question_type == QuestionType.PLUGIN:
                from app.plugins.service import PluginService
                plugin_id = (question_data or {}).get("plugin_id")
                if not plugin_id:
                    raise AppError(status_code=400, code="validation_error", message="PLUGIN question missing data.plugin_id")
                svc = PluginService(self.session)
                
                # Логируем для диагностики
                logger.info(f"PLUGIN answer evaluation: plugin_id={plugin_id}, submitted_answer={req.submitted_answer}")
                
                result = await svc.evaluate_answer(
                    plugin_id=plugin_id,
                    task_id=str(ps.id),
                    user_answer=req.submitted_answer,
                )
                
                # Логируем полный результат от evaluate_answer
                logger.info(
                    f"PLUGIN evaluate_answer returned: "
                    f"result={result}, "
                    f"result_type={type(result)}, "
                    f"result_keys={list(result.keys()) if isinstance(result, dict) else 'not a dict'}"
                )
                
                # Получаем is_correct из результата
                # Проверяем разные возможные ключи
                is_correct = None
                if isinstance(result, dict):
                    is_correct = result.get("correct")
                    if is_correct is None:
                        is_correct = result.get("is_correct")
                    if is_correct is None:
                        is_correct = result.get("isCorrect")
                    if is_correct is None:
                        is_correct = False
                        logger.warning(f"PLUGIN result does not contain 'correct', 'is_correct', or 'isCorrect' key. Result: {result}")
                else:
                    is_correct = False
                    logger.error(f"PLUGIN evaluate_answer returned non-dict result: {result} (type: {type(result)})")
                
                explanation = result.get("explanation", "") if isinstance(result, dict) else ""
                
                # Логируем результат
                logger.info(
                    f"PLUGIN answer result: "
                    f"is_correct={is_correct} (type: {type(is_correct)}), "
                    f"raw_result={result}, "
                    f"explanation={explanation[:100] if explanation else 'None'}"
                )
                
                # Убеждаемся, что is_correct - это булево значение
                if not isinstance(is_correct, bool):
                    logger.warning(f"is_correct is not bool: {is_correct} (type: {type(is_correct)}), converting to bool")
                    if isinstance(is_correct, str):
                        is_correct = is_correct.lower() in ("true", "1", "yes")
                    elif isinstance(is_correct, (int, float)):
                        is_correct = bool(is_correct)
                    else:
                        is_correct = False
                
                logger.info(f"PLUGIN final is_correct: {is_correct} (type: {type(is_correct)})")
            
            # Для вопросов типа "last digit" вычисляем правильный ответ динамически
            # если правильный ответ в базе неправильный
            correct_answer = question.correct_answer.copy() if question.correct_answer else {}
            
            if question.type == QuestionType.MCQ and "last digit" in question.prompt.lower():
                # Извлекаем число из вопроса
                import re
                numbers = re.findall(r'\d+', question.prompt)
                if numbers:
                    number = int(numbers[0])
                    last_digit = str(number % 10)
                    
                    # Находим правильный вариант в choices
                    choices = question.data.get("choices") or question.data.get("options") or []
                    correct_choice_id = None
                    
                    for idx, choice in enumerate(choices):
                        if isinstance(choice, dict):
                            # Проверяем text, value, label
                            choice_text = str(choice.get("text") or choice.get("value") or choice.get("label") or "").strip()
                            choice_id = str(choice.get("id") or "").strip()
                        else:
                            choice_text = str(choice).strip()
                            choice_id = str(idx)
                        
                        if choice_text == last_digit:
                            correct_choice_id = choice_id if choice_id else str(idx)
                            break
                    
                    # Если нашли правильный вариант, обновляем correct_answer
                    if correct_choice_id:
                        correct_answer = {"choice": correct_choice_id}
                        # Логируем исправление
                        import structlog
                        logger = structlog.get_logger()
                        logger.info(
                            "Fixed correct answer for last digit question",
                            question_id=question.id,
                            prompt=question.prompt,
                            number=number,
                            last_digit=last_digit,
                            correct_choice_id=correct_choice_id,
                            original_correct=question.correct_answer,
                        )
                    else:
                        # Правильный ответ отсутствует среди вариантов - это ошибка в данных
                        import structlog
                        logger = structlog.get_logger()
                        logger.error(
                            "Correct answer not found in choices for last digit question",
                            question_id=question.id,
                            prompt=question.prompt,
                            number=number,
                            last_digit=last_digit,
                            choices=choices,
                            current_correct=question.correct_answer,
                        )
                    # Пытаемся найти ближайший вариант или использовать первый
                    # Но лучше всего - исправить вопрос в базе данных
        
        # Для генераторов is_correct уже определен; для PLUGIN — из evaluate; для остальных — _is_correct
        if not is_generator_skill and question_type != QuestionType.PLUGIN:
            # Логируем для отладки MCQ вопросов
            if question_type == QuestionType.MCQ:
                import structlog
                logger = structlog.get_logger()
                logger.info(
                    "MCQ answer check",
                    question_id=req.question_id,
                    submitted=req.submitted_answer,
                    correct=correct_answer,
                    submitted_choice=req.submitted_answer.get("choice"),
                    correct_choice=correct_answer.get("choice"),
                    choices_match=req.submitted_answer.get("choice") == correct_answer.get("choice"),
                )
            is_correct = _is_correct(question_type, question_data, correct_answer, req.submitted_answer)
        else:
            if is_generator_skill:
                logger.info(f"Using is_correct from GeneratorService: {is_correct}")
            elif question_type == QuestionType.PLUGIN:
                # Проверяем, что is_correct был определен в блоке обработки PLUGIN вопросов
                try:
                    # Пытаемся получить значение is_correct
                    is_correct_value = is_correct
                    logger.info(f"Using is_correct from PluginService.evaluate_answer: {is_correct_value} (type: {type(is_correct_value)})")
                except NameError:
                    logger.error(f"is_correct not defined for PLUGIN question! This should not happen. Setting to False.")
                    is_correct = False
                else:
                    # Убеждаемся, что is_correct - это булево значение
                    if not isinstance(is_correct, bool):
                        logger.warning(f"is_correct is not bool for PLUGIN: {is_correct} (type: {type(is_correct)}), converting")
                        if isinstance(is_correct, str):
                            is_correct = is_correct.lower() in ("true", "1", "yes")
                        elif isinstance(is_correct, (int, float)):
                            is_correct = bool(is_correct)
                        else:
                            is_correct = False
                    logger.info(f"PLUGIN is_correct final value: {is_correct} (type: {type(is_correct)})")

        now = utc_now()
        zone_before = ps.current_zone or zone_for_score(ps.current_smartscore)
        streak_before = int(ps.current_streak_correct or 0)
        window = ps.state.get("recent_window") or {"correct": 0, "total": 0}
        stats = WindowStats(correct=int(window.get("correct", 0)), total=int(window.get("total", 0)))
        score_before = int(ps.current_smartscore or 0)
        
        # Логируем состояние перед вычислением SmartScore
        logger.info(
            f"Before SmartScore computation: "
            f"is_correct={is_correct} (type: {type(is_correct)}), "
            f"score_before={score_before}, "
            f"zone_before={zone_before}, "
            f"streak_before={streak_before}, "
            f"question_level={question_level}"
        )
        
        # Отслеживаем серию неправильных ответов
        wrong_streak_before = int(ps.state.get("wrong_streak", 0))
        wrong_streak_after = 0
        if is_correct:
            wrong_streak_after = 0  # Сбрасываем при правильном ответе
        else:
            wrong_streak_after = wrong_streak_before + 1  # Увеличиваем при неправильном
        
        # Убеждаемся, что is_correct - это булево значение
        if not isinstance(is_correct, bool):
            logger.warning(f"is_correct is not bool before SmartScore: {is_correct} (type: {type(is_correct)}), converting")
            is_correct = bool(is_correct)
        
        score_res = compute_next_smartscore(
            current_smartscore=score_before,
            zone=zone_before,
            question_level=question_level,
            is_correct=is_correct,
            current_streak=streak_before,
            wrong_streak=wrong_streak_before,  # Передаем текущее значение до увеличения
            recent_window_stats=stats,
        )
        
        # Логируем результат вычисления SmartScore
        logger.info(
            f"SmartScore computation result: "
            f"smartscore={score_res.smartscore} (was {score_before}), "
            f"streak={score_res.streak} (was {streak_before}), "
            f"zone={score_res.zone} (was {zone_before}), "
            f"is_correct={is_correct} (type: {type(is_correct)}), "
            f"question_type={question_type}, "
            f"is_generator_skill={is_generator_skill}"
        )

        # Если 3 неправильных ответа подряд - завершаем тест
        if wrong_streak_after >= 3:
            logger.info(f"Session {ps.id} finished: 3 wrong answers in a row (questions: {ps.total_questions_answered})")
            ps.finished_at = now
            ps.last_question_id = None
            ps.state["current_question_id"] = None

        # Для генераторов создаем вопрос с данными из q_data
        if is_generator_skill:
            logger.info(f"Creating PracticeAttempt for generator question {req.question_id}")
            # Для генераторов используем данные из q_data
            # Для генераторов question_id = None, так как вопроса нет в базе данных
            import hashlib
            question_id_hash = int(hashlib.md5(str(req.question_id).encode()).hexdigest()[:8], 16) % 1000000
            logger.info(f"Question ID hash: {question_id_hash}, question_level: {question_level}")
            attempt = PracticeAttempt(
                session_id=ps.id,
                user_id=user_uuid,
                skill_id=ps.skill_id,
                question_id=None,  # Для генераторов используем None, так как вопроса нет в БД
                question_level=question_level,
                question_payload={
                    "id": question_id_hash,
                    "skill_id": ps.skill_id,
                    "type": question_type.value,
                    "prompt": q_data.get('prompt', ''),
                    "data": question_data,
                    "correct_answer": correct_answer,
                    "explanation": explanation,
                    "level": question_level,
                },
                submitted_answer=req.submitted_answer,
                is_correct=is_correct,
                mistake_type=None if is_correct else MistakeType.WRONG,
                answered_at=now,
                time_spent_sec=req.time_spent_sec,
                smartscore_before=score_before,
                smartscore_after=score_res.smartscore,
                zone_before=zone_before,
                zone_after=score_res.zone,
            )
            logger.info(f"PracticeAttempt created for generator, adding to database")
        else:
            logger.info(f"Creating PracticeAttempt for regular question {question.id if question else 'None'}")
            # Для обычных вопросов используем данные из question
            attempt = PracticeAttempt(
                session_id=ps.id,
                user_id=user_uuid,
                skill_id=ps.skill_id,
                question_id=question.id,
                question_level=question.level,
                question_payload={
                    "id": question.id,
                    "skill_id": question.skill_id,
                    "type": question.type.value,
                    "prompt": question.prompt,
                    "data": question.data,
                    "correct_answer": question.correct_answer,
                    "explanation": explanation,
                    "level": question.level,
                },
                submitted_answer=req.submitted_answer,
                is_correct=is_correct,
                mistake_type=None if is_correct else MistakeType.WRONG,
                answered_at=now,
                time_spent_sec=req.time_spent_sec,
                smartscore_before=score_before,
                smartscore_after=score_res.smartscore,
                zone_before=zone_before,
                zone_after=score_res.zone,
            )
            # Для обычных вопросов используем данные из question
        attempt = PracticeAttempt(
            session_id=ps.id,
            user_id=user_uuid,
            skill_id=ps.skill_id,
            question_id=question.id,
            question_level=question.level,
            question_payload={
                "id": question.id,
                "skill_id": question.skill_id,
                "type": question.type.value,
                "prompt": question.prompt,
                "data": question.data,
                "correct_answer": question.correct_answer,
                "explanation": explanation,
                "level": question.level,
            },
            submitted_answer=req.submitted_answer,
            is_correct=is_correct,
            mistake_type=None if is_correct else MistakeType.WRONG,
            answered_at=now,
            time_spent_sec=req.time_spent_sec,
            smartscore_before=score_before,
            smartscore_after=score_res.smartscore,
            zone_before=zone_before,
            zone_after=score_res.zone,
        )
        
        logger.info(f"Adding PracticeAttempt to database: session_id={attempt.session_id}, question_id={attempt.question_id}, is_correct={attempt.is_correct}")
        await self.practice.add_attempt(attempt)
        logger.info(f"PracticeAttempt added successfully")

        ps.total_questions_answered += 1
        ps.total_correct += 1 if is_correct else 0
        ps.total_incorrect += 0 if is_correct else 1
        ps.current_streak_correct = score_res.streak
        ps.max_streak_correct = max(int(ps.max_streak_correct or 0), score_res.streak)
        ps.current_smartscore = score_res.smartscore
        ps.current_zone = score_res.zone
        ps.best_smartscore = max(int(ps.best_smartscore or 0), ps.current_smartscore)
        
        # Обновляем серию неправильных ответов в state
        ps.state["wrong_streak"] = wrong_streak_after
        
        # Если SmartScore достиг 100, завершаем тест
        if ps.current_smartscore >= 100:
            logger.info(f"Session {ps.id} finished: SmartScore reached 100 (current: {ps.current_smartscore}, questions: {ps.total_questions_answered})")
            ps.finished_at = now
            ps.last_question_id = None
            ps.state["current_question_id"] = None

        # Update rolling window stats for consistency effects.
        window_total = min(20, int(window.get("total", 0)) + 1)
        window_correct = int(window.get("correct", 0)) + (1 if is_correct else 0)
        if window_total == 20:
            # crude decay once we hit the window size
            window_correct = int(round(window_correct * 0.95))
        ps.state["recent_window"] = {"correct": window_correct, "total": window_total}

        if ps.current_zone == PracticeZone.CHALLENGE and not ps.state.get("entered_challenge_zone_at"):
            ps.state["entered_challenge_zone_at"] = now.isoformat()

        # Backwards compatible mirrors
        ps.questions_answered = ps.total_questions_answered
        ps.correct_count = ps.total_correct
        ps.wrong_count = ps.total_incorrect
        ps.smartscore = ps.current_smartscore
        ps.time_elapsed_sec = ps.active_time_seconds

        snap = await self.practice.get_snapshot(user_id=user_uuid, skill_id=ps.skill_id)
        if snap is None:
            snap = ProgressSnapshot(
                user_id=user_uuid,
                skill_id=ps.skill_id,
                best_smartscore=0,
                last_smartscore=0,
                total_questions=0,
                accuracy_percent=0,
                best_smartscore_all_time=0,
                total_questions_answered_all_time=0,
                total_time_seconds_all_time=0,
            )
        snap.last_practiced_at = now
        snap.last_smartscore = ps.current_smartscore
        snap.best_smartscore = max(int(snap.best_smartscore or 0), ps.current_smartscore)
        snap.best_smartscore_all_time = max(int(snap.best_smartscore_all_time or 0), ps.current_smartscore)
        snap.total_questions_answered_all_time = int(snap.total_questions_answered_all_time or 0) + 1
        snap.total_time_seconds_all_time = int(snap.total_time_seconds_all_time or 0) + int(req.time_spent_sec)

        prev_total = int(snap.total_questions or 0)
        snap.total_questions = prev_total + 1
        prev_correct_est = int(round(prev_total * (int(snap.accuracy_percent or 0) / 100.0)))
        new_correct_est = prev_correct_est + (1 if is_correct else 0)
        snap.accuracy_percent = int(round((new_correct_est / max(1, snap.total_questions)) * 100))
        await self.practice.upsert_snapshot(snap)

        await self._update_assignment_status(student_id=user_uuid, skill_id=ps.skill_id, now=now, session_obj=ps, attempt=attempt)

        finished = ps.finished_at is not None
        if finished:
            logger.info(
                f"Session {ps.id} is finished after submit: "
                f"questions_answered={ps.total_questions_answered}, "
                f"smartscore={ps.current_smartscore}, "
                f"wrong_streak={ps.state.get('wrong_streak', 0)}, "
                f"is_correct={is_correct}"
            )
        
        next_q = None
        # Если тест не завершен, загружаем следующий вопрос
        if not finished:
            if is_generator_skill:
                # Для генераторов создаем новый вопрос
                logger.info("Generating next question for generator skill")
                try:
                    q_data = GeneratorService.execute_generator(
                        skill.generator_code,
                        skill.generator_metadata or {}
                    )
                    # Убеждаемся, что generated_questions существует
                    if 'generated_questions' not in ps.state:
                        ps.state['generated_questions'] = {}
                    # Используем длину словаря для генерации ID
                    question_id = f"generated_{len(ps.state['generated_questions'])}"
                    ps.state['generated_questions'][question_id] = q_data
                    ps.state["current_question_id"] = question_id
                    ps.last_question_id = None
                    # Сохраняем изменения в state
                    await self.session.flush()
                    next_q = _generated_to_question_public(q_data, question_id)
                    logger.info(f"Next question generated: {question_id}")
                except Exception as e:
                    logger.error(f"Error generating next question: {e}", exc_info=True)
                    # Если генератор не работает, пытаемся использовать вопросы из БД
                    try:
                        next_q = await self._select_next_question(ps)
                        if next_q:
                            ps.last_question_id = next_q.id
                            ps.state["current_question_id"] = next_q.id
                            ps.state["recent_question_ids"] = _push_recent(ps.state.get("recent_question_ids", []), next_q.id)
                    except AppError as db_error:
                        logger.error(f"Error getting question from DB: {db_error}", exc_info=True)
                        # Если и из БД не получилось, next_q остается None
            else:
                # Старый способ - получаем вопрос из БД
                # IXL-like: keep session open; prepare next question immediately.
                next_q = await self._select_next_question(ps)
                if next_q:
                    ps.last_question_id = next_q.id
                    ps.state["current_question_id"] = next_q.id
                    ps.state["recent_question_ids"] = _push_recent(ps.state.get("recent_question_ids", []), next_q.id)

        await self.session.flush()

        session_resp = await self._to_session_response(ps, current_question=None)
        # Логируем финальный результат перед возвратом
        logger.info(
            f"Returning PracticeSubmitResponse: "
            f"is_correct={is_correct} (type: {type(is_correct)}), "
            f"finished={ps.finished_at is not None}, "
            f"smartscore={ps.current_smartscore}, "
            f"questions_answered={ps.total_questions_answered}, "
            f"explanation_length={len(explanation) if explanation else 0}"
        )
        
        return PracticeSubmitResponse(
            is_correct=is_correct,
            explanation=(None if is_correct else explanation),
            session=session_resp,
            next_question=_to_question_public(next_q) if next_q is not None else None,
            finished=ps.finished_at is not None,
        )

    async def finish(self, *, user_id, session_id: str) -> None:
        user_uuid = _parse_uuid(user_id)
        ps = await self.practice.get_session(session_id=session_id)
        if ps is None or ps.user_id != user_uuid:
            raise AppError(status_code=404, code="not_found", message="Session not found")
        if ps.finished_at is not None:
            return
        ps.finished_at = utc_now()
        ps.last_question_id = None
        ps.state["current_question_id"] = None
        await self.session.flush()

    async def _select_next_question(self, session_obj: PracticeSession):
        desired_levels = _level_search_order(3 if session_obj.current_zone == PracticeZone.CHALLENGE else 2)
        recent = session_obj.state.get("recent_question_ids") or []
        recent_ids = [int(x) for x in recent if isinstance(x, int)]

        candidates = await self.questions.list_for_skill_levels(
            skill_id=session_obj.skill_id,
            levels=desired_levels,
            exclude_ids=recent_ids,
            limit=1,
        )
        if candidates:
            return candidates[0]

        # If we've exhausted unique questions, allow repeats.
        candidates = await self.questions.list_for_skill_levels(
            skill_id=session_obj.skill_id,
            levels=desired_levels,
            exclude_ids=[],
            limit=1,
        )
        if not candidates:
            raise AppError(status_code=404, code="not_found", message="No questions available for this skill")
        return candidates[0]

    async def _to_session_response(self, ps: PracticeSession, current_question=None) -> PracticeSessionResponse:
        # Проверяем тип вопроса - если это QuestionPublic, используем напрямую, иначе конвертируем
        if current_question is None:
            q = None
        elif isinstance(current_question, QuestionPublic):
            q = current_question
        else:
            try:
                q = _to_question_public(current_question)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error converting question to public format: {e}", exc_info=True)
                q = None
        return PracticeSessionResponse(
            id=str(ps.id),
            skill_id=ps.skill_id,
            started_at=ps.started_at,
            finished_at=ps.finished_at,
            questions_answered=ps.questions_answered,
            correct_count=ps.correct_count,
            wrong_count=ps.wrong_count,
            smartscore=ps.smartscore,
            time_elapsed_sec=ps.time_elapsed_sec,
            state=ps.state,
            current_question=q,
            current_smartscore=ps.current_smartscore,
            best_smartscore=ps.best_smartscore,
            total_questions_answered=ps.total_questions_answered,
            total_correct=ps.total_correct,
            total_incorrect=ps.total_incorrect,
            current_streak_correct=ps.current_streak_correct,
            max_streak_correct=ps.max_streak_correct,
            current_zone=ps.current_zone.value if ps.current_zone else None,
            last_question_id=ps.last_question_id,
            last_activity_at=ps.last_activity_at,
            active_time_seconds=ps.active_time_seconds,
            inactivity_threshold_seconds=ps.inactivity_threshold_seconds,
        )

    async def _enforce_subscription_limit(self, *, user_id: uuid.UUID) -> None:
        # Проверяем роль пользователя - ADMIN и TEACHER имеют полный доступ
        from app.repositories.user_repo import UserRepository
        user_repo = UserRepository(self.session)
        user = await user_repo.get_by_id(user_id)
        if user and user.role in ("ADMIN", "TEACHER"):
            return
        
        # Проверяем подписку
        sub = await self.subscriptions.get_for_user(user_id)
        if sub and sub.plan == SubscriptionPlan.PREMIUM and sub.is_active:
            return

        # Логируем для отладки, если подписка не найдена или неактивна
        import structlog
        logger = structlog.get_logger()
        logger.warning(
            "Subscription check failed",
            user_id=str(user_id),
            has_subscription=sub is not None,
            plan=sub.plan.value if sub else None,
            is_active=sub.is_active if sub else None,
        )

        # Для пользователей без подписки применяем лимит бесплатных вопросов
        redis = get_redis()
        date_key = utc_now().date().isoformat()
        key = f"usage:questions:{user_id}:{date_key}"
        count = await redis.incr(key)
        if count == 1:
            # Expire at next UTC midnight.
            tomorrow = datetime.combine(utc_now().date(), datetime.min.time(), tzinfo=utc_now().tzinfo).timestamp() + 86400
            ttl = int(tomorrow - utc_now().timestamp())
            await redis.expire(key, max(60, ttl))
        if count > settings.free_daily_question_limit:
            raise AppError(status_code=402, code="subscription_required", message="Daily free question limit exceeded")

    async def heartbeat(self, *, user_id, session_id: str) -> PracticeSessionResponse:
        user_uuid = _parse_uuid(user_id)
        ps = await self.practice.get_session(session_id=session_id)
        if ps is None or ps.user_id != user_uuid:
            raise AppError(status_code=404, code="not_found", message="Session not found")
        if ps.finished_at is not None:
            return await self._to_session_response(ps, current_question=None)
        await self._touch_activity(ps)
        q = await self.questions.get(ps.last_question_id) if ps.last_question_id else None
        return await self._to_session_response(ps, current_question=q)

    async def _touch_activity(self, ps: PracticeSession) -> None:
        new_active, new_last = apply_active_time_delta(
            last_activity_at=ps.last_activity_at,
            inactivity_threshold_seconds=ps.inactivity_threshold_seconds,
            current_active_time_seconds=ps.active_time_seconds,
        )
        ps.active_time_seconds = new_active
        ps.last_activity_at = new_last
        ps.time_elapsed_sec = ps.active_time_seconds

    async def _update_assignment_status(
        self,
        *,
        student_id: uuid.UUID,
        skill_id: int,
        now: datetime,
        session_obj: PracticeSession,
        attempt: PracticeAttempt,
    ) -> None:
        rows = await self.assignments.list_active_for_student_skill(student_id=student_id, skill_id=skill_id)
        for assignment, status_row in rows:
            if status_row.status == AssignmentStatus.NOT_STARTED:
                status_row.status = AssignmentStatus.IN_PROGRESS
            status_row.last_smartscore = session_obj.current_smartscore
            status_row.best_smartscore = max(int(status_row.best_smartscore or 0), int(session_obj.best_smartscore or 0))
            status_row.questions_answered = int(status_row.questions_answered or 0) + 1
            status_row.time_spent_seconds = int(getattr(status_row, "time_spent_seconds", 0) or 0) + int(attempt.time_spent_sec or 0)
            status_row.last_activity_at = now
            if status_row.best_smartscore >= int(assignment.target_smartscore or 80):
                status_row.status = AssignmentStatus.COMPLETED
                status_row.completed_at = now


def _is_expired(last_activity_at: datetime) -> bool:
    return (utc_now() - last_activity_at).total_seconds() > (settings.practice_session_expiry_hours * 3600)


def _parse_uuid(value) -> uuid.UUID:
    try:
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
    except ValueError as e:
        raise AppError(status_code=400, code="validation_error", message="Invalid id") from e


def _push_recent(recent: list[Any], qid: int, max_len: int = 20) -> list[int]:
    out: list[int] = [int(x) for x in recent if isinstance(x, int) and int(x) != qid]
    out.insert(0, qid)
    return out[:max_len]


def _level_search_order(difficulty: int) -> list[int]:
    difficulty = max(1, min(5, difficulty))
    order = [difficulty]
    for delta in range(1, 5):
        hi = difficulty + delta
        lo = difficulty - delta
        if hi <= 5:
            order.append(hi)
        if lo >= 1:
            order.append(lo)
    return order


def _to_question_public(q) -> QuestionPublic:
    return QuestionPublic(id=q.id, skill_id=q.skill_id, type=q.type, prompt=q.prompt, data=q.data, level=q.level)


def _generated_to_question_public(q_data: dict[str, Any], question_id: str) -> QuestionPublic:
    """Преобразует сгенерированный вопрос в QuestionPublic"""
    from app.models.enums import QuestionType
    # Для генераторов используем хеш ID как числовой идентификатор
    import hashlib
    id_hash = int(hashlib.md5(question_id.encode()).hexdigest()[:8], 16) % 1000000
    
    # Сохраняем оригинальный ID генератора в data, чтобы фронтенд мог его использовать
    question_data = q_data.get('data', {}).copy()
    question_data['_generator_id'] = question_id  # Сохраняем оригинальный ID генератора
    
    return QuestionPublic(
        id=id_hash,
        skill_id=0,  # Будет установлено из сессии
        type=QuestionType(q_data.get('type', 'MCQ')),
        prompt=q_data.get('prompt', ''),
        data=question_data,
        level=q_data.get('level', 1)
    )


def _validate_submitted_answer(qtype: QuestionType, data: dict[str, Any], submitted: dict[str, Any]) -> None:
    if not isinstance(submitted, dict):
        raise AppError(status_code=400, code="validation_error", message="submitted_answer must be an object")

    if qtype == QuestionType.MCQ:
        if not isinstance(submitted.get("choice"), str):
            raise AppError(status_code=400, code="validation_error", message="MCQ submitted_answer.choice must be a string")
    elif qtype == QuestionType.MULTI_SELECT:
        choices = submitted.get("choices")
        if not isinstance(choices, list) or not all(isinstance(x, str) for x in choices):
            raise AppError(status_code=400, code="validation_error", message="MULTI_SELECT submitted_answer.choices must be a list of strings")
    elif qtype == QuestionType.NUMERIC:
        value = submitted.get("value")
        if not isinstance(value, (int, float)):
            raise AppError(status_code=400, code="validation_error", message="NUMERIC submitted_answer.value must be a number")
    elif qtype == QuestionType.TEXT:
        if not isinstance(submitted.get("text"), str):
            raise AppError(status_code=400, code="validation_error", message="TEXT submitted_answer.text must be a string")
    elif qtype in (QuestionType.INTERACTIVE, QuestionType.PLUGIN):
        if not isinstance(submitted, dict):
            raise AppError(status_code=400, code="validation_error", message="PLUGIN/INTERACTIVE submitted_answer must be an object")
    else:
        raise AppError(status_code=400, code="validation_error", message="Unsupported question type")


def _is_correct(qtype: QuestionType, data: dict[str, Any], correct: dict[str, Any], submitted: dict[str, Any]) -> bool:
    if qtype == QuestionType.MCQ:
        submitted_choice = submitted.get("choice")
        correct_choice = correct.get("choice")
        
        # Нормализуем значения для сравнения (приводим к строкам и убираем пробелы)
        if submitted_choice is not None and correct_choice is not None:
            # Приводим к строкам и сравниваем (без учета регистра для буквенных вариантов)
            sub_str = str(submitted_choice).strip()
            cor_str = str(correct_choice).strip()
            
            # Прямое сравнение
            if sub_str == cor_str:
                return True
            
            # Если не совпало, проверяем, может быть правильный ответ - это индекс варианта
            # Или наоборот, отправленный ответ нужно сравнить с вариантом по индексу
            choices = data.get("choices") or data.get("options") or []
            
            # Проверяем, может быть correct_choice - это индекс
            try:
                correct_idx = int(cor_str)
                if 0 <= correct_idx < len(choices):
                    correct_value = choices[correct_idx]
                    # Нормализуем значение варианта
                    if isinstance(correct_value, dict):
                        correct_value_str = str(correct_value.get("value") or correct_value.get("label") or correct_value.get("text") or "").strip()
                    else:
                        correct_value_str = str(correct_value).strip()
                    if sub_str == correct_value_str:
                        return True
            except (ValueError, TypeError, IndexError):
                pass
            
            # Проверяем, может быть submitted_choice нужно сравнить с вариантом по индексу
            try:
                submitted_idx = int(sub_str)
                if 0 <= submitted_idx < len(choices):
                    submitted_value = choices[submitted_idx]
                    if isinstance(submitted_value, dict):
                        submitted_value_str = str(submitted_value.get("value") or submitted_value.get("label") or submitted_value.get("text") or "").strip()
                    else:
                        submitted_value_str = str(submitted_value).strip()
                    if cor_str == submitted_value_str:
                        return True
            except (ValueError, TypeError, IndexError):
                pass
            
            # Проверяем, может быть нужно сравнить значения вариантов напрямую
            for idx, choice in enumerate(choices):
                if isinstance(choice, dict):
                    choice_str = str(choice.get("value") or choice.get("label") or choice.get("text") or "").strip()
                else:
                    choice_str = str(choice).strip()
                
                # Если отправленный ответ совпадает с вариантом, проверяем, является ли этот вариант правильным
                if sub_str == choice_str:
                    # Правильный ответ может быть индексом или значением
                    if str(idx) == cor_str or choice_str == cor_str:
                        return True
        
        # Если одно из значений None, возвращаем False
        return False
    if qtype == QuestionType.MULTI_SELECT:
        return set(submitted.get("choices") or []) == set(correct.get("choices") or [])
    if qtype == QuestionType.NUMERIC:
        tol = float(data.get("tolerance") or 0)
        try:
            return abs(float(submitted.get("value")) - float(correct.get("value"))) <= tol
        except (TypeError, ValueError):
            return False
    if qtype == QuestionType.TEXT:
        s = (submitted.get("text") or "").strip().lower()
        c = (correct.get("text") or "").strip().lower()
        return s == c
    return False
