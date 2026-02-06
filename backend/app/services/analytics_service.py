from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.assignment import Assignment, AssignmentStatusRow
from app.models.classroom import Classroom, Enrollment
from app.models.enums import AssignmentStatus
from app.models.practice import PracticeAttempt, PracticeSession, ProgressSnapshot
from app.models.user import User


class AnalyticsService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def overview(self, *, user_id: str) -> dict[str, Any]:
        uid = _parse_uuid(user_id)

        time_stmt = select(func.coalesce(func.sum(PracticeSession.time_elapsed_sec), 0)).where(PracticeSession.user_id == uid)
        total_time = int((await self.session.execute(time_stmt)).scalar_one())

        skills_stmt = select(func.count(func.distinct(PracticeSession.skill_id))).where(PracticeSession.user_id == uid)
        skills_practiced = int((await self.session.execute(skills_stmt)).scalar_one())

        attempts_stmt = (
            select(
                func.count(PracticeAttempt.id),
                func.coalesce(func.sum(case((PracticeAttempt.is_correct.is_(True), 1), else_=0)), 0),
            )
            .select_from(PracticeAttempt)
            .join(PracticeSession, PracticeSession.id == PracticeAttempt.session_id)
            .where(PracticeSession.user_id == uid)
        )
        total_attempts, correct_attempts = (await self.session.execute(attempts_stmt)).one()
        total_attempts = int(total_attempts)
        correct_attempts = int(correct_attempts)
        avg_accuracy = int(round((correct_attempts / max(1, total_attempts)) * 100))

        return {
            "total_time_sec": total_time,
            "skills_practiced": skills_practiced,
            "avg_accuracy_percent": avg_accuracy,
            "total_questions_answered": total_attempts,
        }

    async def skills(self, *, user_id: str) -> list[dict[str, Any]]:
        uid = _parse_uuid(user_id)
        
        # Import Skill model for join
        from app.models.catalog import Skill, Grade
        
        stmt = (
            select(
                ProgressSnapshot.skill_id,
                ProgressSnapshot.best_smartscore,
                ProgressSnapshot.last_smartscore,
                ProgressSnapshot.last_practiced_at,
                ProgressSnapshot.total_questions,
                ProgressSnapshot.accuracy_percent,
                Skill.title.label('skill_name'),
                Skill.grade_id,
                Grade.number.label('grade_number'),
            )
            .join(Skill, Skill.id == ProgressSnapshot.skill_id)
            .join(Grade, Grade.id == Skill.grade_id)
            .where(ProgressSnapshot.user_id == uid)
            .order_by(ProgressSnapshot.last_practiced_at.desc().nullslast())
        )
        rows = (await self.session.execute(stmt)).all()
        
        # Получаем общее время для каждого навыка из сессий
        result = []
        for r in rows:
            # Суммируем время из всех сессий для этого навыка
            time_stmt = (
                select(func.coalesce(func.sum(PracticeSession.active_time_seconds), 0))
                .where(PracticeSession.user_id == uid, PracticeSession.skill_id == r.skill_id)
            )
            total_time = int((await self.session.execute(time_stmt)).scalar_one())
            
            result.append({
                "skill_id": r.skill_id,
                "skill_name": r.skill_name,
                "grade_id": r.grade_id,
                "grade_number": r.grade_number,
                "best_smartscore": r.best_smartscore,
                "last_smartscore": r.last_smartscore,
                "last_practiced_at": r.last_practiced_at,
                "total_questions": r.total_questions,
                "accuracy_percent": r.accuracy_percent,
                "total_time_seconds": total_time,
            })
        
        return result

    async def all_questions(self, *, user_id: str) -> list[dict[str, Any]]:
        """Получить все вопросы с ответами пользователя, отсортированные по правильности"""
        uid = _parse_uuid(user_id)
        attempts_stmt = (
            select(PracticeAttempt, PracticeSession)
            .join(PracticeSession, PracticeSession.id == PracticeAttempt.session_id)
            .where(PracticeAttempt.user_id == uid)
            .order_by(PracticeAttempt.answered_at.desc())
        )
        rows = (await self.session.execute(attempts_stmt)).all()
        
        questions = []
        for attempt, sess in rows:
            question_payload = attempt.question_payload or {}
            question_data = question_payload.get("data") or {}
            question_type = question_payload.get("type", "")
            
            # Форматируем ответ пользователя
            user_answer_text = ""
            if attempt.submitted_answer:
                if "choice" in attempt.submitted_answer:
                    choice_id = attempt.submitted_answer["choice"]
                    # Для MCQ пытаемся найти текст варианта
                    if question_type == "MCQ" and "choices" in question_data:
                        choices = question_data["choices"]
                        for choice in choices:
                            if isinstance(choice, dict) and str(choice.get("id")) == str(choice_id):
                                user_answer_text = choice.get("label") or choice.get("text") or choice.get("value") or str(choice_id)
                                break
                        if not user_answer_text:
                            user_answer_text = str(choice_id)
                    else:
                        user_answer_text = str(choice_id)
                elif "value" in attempt.submitted_answer:
                    user_answer_text = str(attempt.submitted_answer["value"])
                elif "answer" in attempt.submitted_answer:
                    user_answer_text = str(attempt.submitted_answer["answer"])
                else:
                    user_answer_text = json.dumps(attempt.submitted_answer)
            
            # Форматируем правильный ответ
            correct_answer_text = ""
            # Сначала проверяем correct_answer в question_payload
            correct_answer = question_payload.get("correct_answer") or {}
            if correct_answer:
                if "choice" in correct_answer:
                    choice_id = correct_answer["choice"]
                    if question_type == "MCQ" and "choices" in question_data:
                        choices = question_data["choices"]
                        for choice in choices:
                            if isinstance(choice, dict) and str(choice.get("id")) == str(choice_id):
                                correct_answer_text = choice.get("label") or choice.get("text") or choice.get("value") or str(choice_id)
                                break
                        if not correct_answer_text:
                            correct_answer_text = str(choice_id)
                    else:
                        correct_answer_text = str(choice_id)
                elif "value" in correct_answer:
                    correct_answer_text = str(correct_answer["value"])
                elif "answer" in correct_answer:
                    correct_answer_text = str(correct_answer["answer"])
                else:
                    correct_answer_text = json.dumps(correct_answer)
            # Если не нашли в correct_answer, проверяем question_data
            elif question_data:
                if "correct_answer" in question_data:
                    correct_answer_text = str(question_data["correct_answer"])
                elif "answer" in question_data:
                    answer = question_data["answer"]
                    if isinstance(answer, (int, float)):
                        correct_answer_text = str(answer)
                    elif isinstance(answer, dict):
                        if "choice" in answer:
                            choice_id = answer["choice"]
                            if question_type == "MCQ" and "choices" in question_data:
                                choices = question_data["choices"]
                                for choice in choices:
                                    if isinstance(choice, dict) and str(choice.get("id")) == str(choice_id):
                                        correct_answer_text = choice.get("label") or choice.get("text") or choice.get("value") or str(choice_id)
                                        break
                                if not correct_answer_text:
                                    correct_answer_text = str(choice_id)
                            else:
                                correct_answer_text = str(choice_id)
                        else:
                            correct_answer_text = json.dumps(answer)
                    else:
                        correct_answer_text = str(answer)
                elif "correct_index" in question_data and "choices" in question_data:
                    # Для MCQ с correct_index
                    idx = question_data["correct_index"]
                    choices = question_data["choices"]
                    if isinstance(idx, int) and 0 <= idx < len(choices):
                        choice = choices[idx]
                        if isinstance(choice, dict):
                            correct_answer_text = choice.get("label") or choice.get("text") or choice.get("value") or str(choice)
                        else:
                            correct_answer_text = str(choice)
            
            # Для PLUGIN вопросов передаём полный submitted_answer (содержит questionData, answerData)
            if question_type in ("PLUGIN", "INTERACTIVE"):
                user_answer_raw = attempt.submitted_answer
            else:
                user_answer_raw = user_answer_text
            
            questions.append({
                "attempt_id": str(attempt.id),
                "question_id": attempt.question_id,
                "skill_id": attempt.skill_id,
                "question_prompt": question_payload.get("prompt", ""),
                "question_type": question_payload.get("type", ""),
                "user_answer": user_answer_raw,  # Для PLUGIN - объект с questionData, для остальных - строка
                "correct_answer": correct_answer_text,
                "is_correct": attempt.is_correct,
                "answered_at": attempt.answered_at,
                "time_spent_seconds": attempt.time_spent_sec,
                "smartscore_before": attempt.smartscore_before,
                "smartscore_after": attempt.smartscore_after,
            })
        
        return questions

    async def classroom_analytics(self, *, teacher_id: str, classroom_id: str) -> dict[str, Any]:
        tid = _parse_uuid(teacher_id)
        cid = _parse_uuid(classroom_id)
        classroom = await self.session.get(Classroom, cid)
        if classroom is None or classroom.teacher_id != tid:
            raise AppError(status_code=404, code="not_found", message="Classroom not found")

        enroll_stmt = select(Enrollment.student_id).where(Enrollment.classroom_id == cid)
        student_ids = [row.student_id for row in (await self.session.execute(enroll_stmt)).all()]

        students: list[dict[str, Any]] = []
        for sid in student_ids:
            user = await self.session.get(User, sid)
            if user is None:
                continue
            snap_stmt = select(func.coalesce(func.avg(ProgressSnapshot.best_smartscore), 0)).where(ProgressSnapshot.user_id == sid)
            avg_best = int(round(float((await self.session.execute(snap_stmt)).scalar_one())))

            assign_stmt = (
                select(
                    func.count(AssignmentStatusRow.id),
                    func.coalesce(
                        func.sum(case((AssignmentStatusRow.status == AssignmentStatus.COMPLETED, 1), else_=0)),
                        0,
                    ),
                )
                .select_from(AssignmentStatusRow)
                .join(Assignment, Assignment.id == AssignmentStatusRow.assignment_id)
                .where(Assignment.classroom_id == cid, AssignmentStatusRow.student_id == sid)
            )
            total_assign, completed_assign = (await self.session.execute(assign_stmt)).one()
            students.append(
                {
                    "student_id": str(sid),
                    "email": user.email,
                    "full_name": user.full_name,
                    "avg_best_smartscore": avg_best,
                    "assignments_total": int(total_assign),
                    "assignments_completed": int(completed_assign),
                }
            )

        classroom_avg = int(round(sum(s["avg_best_smartscore"] for s in students) / max(1, len(students))))
        return {
            "classroom_id": str(cid),
            "title": classroom.title,
            "student_count": len(students),
            "avg_best_smartscore": classroom_avg,
            "students": students,
        }

    async def questions_log(
        self,
        *,
        requester_id: str,
        requester_role: str,
        skill_id: int,
        student_id: str | None = None,
    ) -> dict[str, Any]:
        rid = _parse_uuid(requester_id)
        sid = _parse_uuid(student_id) if student_id else rid

        if sid != rid and requester_role not in {"TEACHER", "ADMIN"}:
            raise AppError(status_code=403, code="forbidden", message="Insufficient permissions")

        if requester_role == "TEACHER" and sid != rid:
            # Ensure teacher has this student enrolled in any of their classrooms.
            stmt = (
                select(func.count())
                .select_from(Enrollment)
                .join(Classroom, Classroom.id == Enrollment.classroom_id)
                .where(Classroom.teacher_id == rid, Enrollment.student_id == sid)
            )
            if int((await self.session.execute(stmt)).scalar_one()) == 0:
                raise AppError(status_code=403, code="forbidden", message="Student not in your classrooms")

        attempts_stmt = (
            select(PracticeAttempt, PracticeSession)
            .join(PracticeSession, PracticeSession.id == PracticeAttempt.session_id)
            .where(PracticeAttempt.user_id == sid, PracticeAttempt.skill_id == skill_id)
            .order_by(PracticeAttempt.answered_at.asc())
        )
        rows = (await self.session.execute(attempts_stmt)).all()

        sessions: dict[str, dict[str, Any]] = {}
        for attempt, sess in rows:
            key = str(sess.id)
            if key not in sessions:
                sessions[key] = {
                    "session_id": key,
                    "started_at": sess.started_at,
                    "finished_at": sess.finished_at,
                    "current_smartscore": sess.current_smartscore,
                    "best_smartscore": sess.best_smartscore,
                    "active_time_seconds": sess.active_time_seconds,
                    "attempts": [],
                }
            sessions[key]["attempts"].append(
                {
                    "attempt_id": str(attempt.id),
                    "question_id": attempt.question_id,
                    "question_level": attempt.question_level,
                    "question_payload": attempt.question_payload,
                    "submitted_answer": attempt.submitted_answer,
                    "is_correct": attempt.is_correct,
                    "mistake_type": attempt.mistake_type.value if attempt.mistake_type else None,
                    "answered_at": attempt.answered_at,
                    "time_spent_seconds_for_question": attempt.time_spent_sec,
                    "smartscore_before": attempt.smartscore_before,
                    "smartscore_after": attempt.smartscore_after,
                    "zone_before": attempt.zone_before.value if hasattr(attempt.zone_before, "value") else str(attempt.zone_before),
                    "zone_after": attempt.zone_after.value if hasattr(attempt.zone_after, "value") else str(attempt.zone_after),
                }
            )

        summary_stmt = (
            select(
                func.coalesce(func.count(PracticeAttempt.id), 0),
                func.coalesce(func.sum(case((PracticeAttempt.is_correct.is_(True), 1), else_=0)), 0),
                func.coalesce(func.sum(PracticeAttempt.time_spent_sec), 0),
            )
            .where(PracticeAttempt.user_id == sid, PracticeAttempt.skill_id == skill_id)
        )
        total_attempts, total_correct, total_time = (await self.session.execute(summary_stmt)).one()
        accuracy = int(round((int(total_correct) / max(1, int(total_attempts))) * 100))

        snap_stmt = select(ProgressSnapshot).where(ProgressSnapshot.user_id == sid, ProgressSnapshot.skill_id == skill_id)
        snap = (await self.session.execute(snap_stmt)).scalar_one_or_none()

        return {
            "student_id": str(sid),
            "skill_id": skill_id,
            "summary": {
                "total_questions_answered": int(total_attempts),
                "accuracy_percent": accuracy,
                "total_time_seconds": int(total_time),
                "last_smartscore": snap.last_smartscore if snap else 0,
                "best_smartscore_all_time": (snap.best_smartscore_all_time if snap else 0),
                "last_practiced_at": snap.last_practiced_at if snap else None,
            },
            "sessions": list(sessions.values()),
        }


def _parse_uuid(value) -> uuid.UUID:
    try:
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
    except ValueError as e:
        raise AppError(status_code=400, code="validation_error", message="Invalid id") from e
