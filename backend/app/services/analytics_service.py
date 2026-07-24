from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import Depends  # type: ignore
from sqlalchemy import case, func, select  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from app.core.errors import AppError  # type: ignore
from app.db.session import get_db_session  # type: ignore
from app.models.assignment import Assignment, AssignmentStatusRow  # type: ignore
from app.models.classroom import Classroom, Enrollment  # type: ignore
from app.models.enums import AssignmentStatus, UserRole  # type: ignore
from app.models.practice import PracticeAttempt, PracticeSession, ProgressSnapshot  # type: ignore
from app.models.user import User  # type: ignore
from app.services.teacher_scope import list_teacher_scoped_students


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _choice_label(choice_id: Any, *, question_type: str, question_data: dict[str, Any]) -> str:
    if question_type == "MCQ":
        for choice in _as_list(question_data.get("choices")):
            if isinstance(choice, dict) and str(choice.get("id")) == str(choice_id):
                return str(choice.get("label") or choice.get("text") or choice.get("value") or choice_id)
    return str(choice_id)


def _stringify_answer_value(answer: Any, *, question_type: str, question_data: dict[str, Any]) -> str:
    if isinstance(answer, dict):
        if "choice" in answer:
            return _choice_label(answer.get("choice"), question_type=question_type, question_data=question_data)
        if "text" in answer:
            return str(answer.get("text"))
        if "userAnswer" in answer:
            return str(answer.get("userAnswer"))
        if "studentAnswer" in answer:
            return str(answer.get("studentAnswer"))
        if "answer" in answer:
            nested = answer.get("answer")
            return str(nested) if isinstance(nested, (str, int, float, bool)) else _safe_json_dumps(nested)
        return _safe_json_dumps(answer)
    if answer in (None, ""):
        return ""
    if isinstance(answer, (str, int, float, bool)):
        return str(answer)
    return _safe_json_dumps(answer)


def _extract_correct_answer_text(question_payload: dict[str, Any], question_data: dict[str, Any], question_type: str) -> str:
    correct_answer = question_payload.get("correct_answer")
    if correct_answer:
        return _stringify_answer_value(correct_answer, question_type=question_type, question_data=question_data)

    fallback_answer = question_data.get("correct_answer")
    if fallback_answer is not None:
        return _stringify_answer_value(fallback_answer, question_type=question_type, question_data=question_data)

    answer = question_data.get("answer")
    if answer is not None:
        return _stringify_answer_value(answer, question_type=question_type, question_data=question_data)

    correct_index = question_data.get("correct_index")
    choices = _as_list(question_data.get("choices"))
    if isinstance(correct_index, int) and 0 <= correct_index < len(choices):
        choice = choices[correct_index]
        if isinstance(choice, dict):
            return str(choice.get("label") or choice.get("text") or choice.get("value") or choice)
        return str(choice)

    return ""


def _serialize_attempt_question(attempt: PracticeAttempt) -> dict[str, Any]:
    question_payload = _as_dict(attempt.question_payload)
    question_data = _as_dict(question_payload.get("data"))
    question_type = str(question_payload.get("type", "") or "")
    user_answer_text = _stringify_answer_value(
        attempt.submitted_answer,
        question_type=question_type,
        question_data=question_data,
    )
    correct_answer_text = _extract_correct_answer_text(question_payload, question_data, question_type)
    prompt = question_payload.get("prompt", "")

    # For PLUGIN/INTERACTIVE questions, extract the actual question text and parameters
    # from submitted_answer (the plugin sends question, questionData, etc.)
    submitted = _as_dict(attempt.submitted_answer)
    submitted_qdata = _as_dict(submitted.get("questionData") or submitted.get("visualData"))

    if question_type in ("PLUGIN", "INTERACTIVE"):
        plugin_question = submitted.get("question") or submitted.get("prompt") or submitted.get("questionText") or submitted_qdata.get("question")
        if plugin_question:
            prompt = plugin_question

        seed = question_data.get("seed") or question_payload.get("seed") or submitted.get("seed") or submitted_qdata.get("seed")
        level = question_data.get("level") or question_payload.get("level") or submitted_qdata.get("level") or attempt.question_level

        question_data = {**submitted_qdata, **question_data}
        if seed is not None:
            question_data["seed"] = seed
        if level is not None:
            question_data["level"] = level
    else:
        seed = question_data.get("seed") or question_payload.get("seed")
        level = question_data.get("level") or question_payload.get("level") or attempt.question_level

    return {
        "attempt_id": str(attempt.id),
        "question_id": attempt.question_id,
        "skill_id": attempt.skill_id,
        "user_id": str(attempt.user_id),
        "question_prompt": prompt if isinstance(prompt, str) else str(prompt),
        "question_type": question_type,
        "question_data": question_data,
        "user_answer": attempt.submitted_answer if question_type in ("PLUGIN", "INTERACTIVE") else user_answer_text,
        "correct_answer": correct_answer_text,
        "is_correct": attempt.is_correct,
        "answered_at": attempt.answered_at,
        "time_spent_seconds": attempt.time_spent_sec,
        "smartscore_before": attempt.smartscore_before,
        "smartscore_after": attempt.smartscore_after,
        "seed": seed,
        "level": level,
    }


class AnalyticsService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def overview(self, *, user_id: str) -> dict[str, Any]:
        uid = _parse_uuid(user_id)

        time_stmt = select(func.coalesce(func.sum(PracticeSession.time_elapsed_sec), 0)).where(PracticeSession.user_id == uid)
        total_time = int((await self.session.execute(time_stmt)).scalar_one())

        skills_stmt = select(func.count(func.distinct(PracticeSession.skill_id))).where(
            PracticeSession.user_id == uid,
            PracticeSession.total_questions_answered > 0
        )
        skills_practiced = int((await self.session.execute(skills_stmt)).scalar_one())

        attempts_stmt = (
            select(
                func.count(PracticeAttempt.id),
                func.coalesce(func.sum(case((PracticeAttempt.is_correct.is_(True), 1), else_=0)), 0),
            )
            .select_from(PracticeAttempt)
            .where(PracticeAttempt.user_id == uid)
        )
        total_attempts, correct_attempts = (await self.session.execute(attempts_stmt)).one()
        total_attempts = int(total_attempts)
        avg_accuracy = round((correct_attempts / max(1, total_attempts)) * 100)

        # Get total skills by grade
        # We need to import Skill and Grade inside the method to avoid circular imports if they are not already imported at top level
        # Based on previous file view, they were imported inside `skills` method, so we should do same or import at top if possible.
        # Checking file content again, they are not imported at top level.
        from app.models.catalog import Skill, Grade  # type: ignore

        skills_by_grade_stmt = (
            select(Grade.number, func.count(Skill.id))
            .join(Skill.grade)
            .where(Skill.is_published.is_(True))
            .group_by(Grade.number)
        )
        skills_by_grade_rows = (await self.session.execute(skills_by_grade_stmt)).all()
        total_skills_by_grade = {row[0]: row[1] for row in skills_by_grade_rows}

        return {
            "total_time_sec": total_time,
            "skills_practiced": skills_practiced,
            "avg_accuracy_percent": avg_accuracy,
            "total_questions_answered": total_attempts,
            "total_skills_by_grade": total_skills_by_grade,
        }

    async def skills(self, *, user_id: str) -> list[dict[str, Any]]:
        uid = _parse_uuid(user_id)
        
        # Import Skill model for join
        from app.models.catalog import Skill, Grade  # type: ignore
        from app.models.topic import Topic  # type: ignore
        
        time_by_skill = (
            select(
                PracticeSession.skill_id.label("skill_id"),
                func.coalesce(func.sum(PracticeSession.active_time_seconds), 0).label("total_time_seconds"),
            )
            .where(PracticeSession.user_id == uid)
            .group_by(PracticeSession.skill_id)
            .subquery()
        )

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
                Skill.topic_id,
                Grade.number.label('grade_number'),
                Topic.title.label('topic_title'),
                func.coalesce(time_by_skill.c.total_time_seconds, 0).label("total_time_seconds"),
            )
            .join(Skill, Skill.id == ProgressSnapshot.skill_id)
            .join(Grade, Grade.id == Skill.grade_id)
            .outerjoin(Topic, Topic.id == Skill.topic_id)
            .outerjoin(time_by_skill, time_by_skill.c.skill_id == ProgressSnapshot.skill_id)
            .where(ProgressSnapshot.user_id == uid)
            .order_by(ProgressSnapshot.last_practiced_at.desc().nullslast())
        )
        rows = (await self.session.execute(stmt)).all()

        result = []
        for r in rows:
            result.append({
                "skill_id": r.skill_id,
                "skill_name": r.skill_name,
                "grade_id": r.grade_id,
                "grade_number": r.grade_number,
                "topic_id": r.topic_id,
                "topic_title": r.topic_title,
                "best_smartscore": r.best_smartscore,
                "last_smartscore": r.last_smartscore,
                "last_practiced_at": r.last_practiced_at,
                "total_questions": r.total_questions,
                "accuracy_percent": r.accuracy_percent,
                "total_time_seconds": int(r.total_time_seconds or 0),
            })
        
        return result

    async def all_questions(self, *, user_id: str) -> list[dict[str, Any]]:
        """Получить все вопросы с ответами пользователя, отсортированные по правильности"""
        uid = _parse_uuid(user_id)
        attempts_stmt = select(PracticeAttempt).where(PracticeAttempt.user_id == uid).order_by(PracticeAttempt.answered_at.desc())
        rows = (await self.session.execute(attempts_stmt)).all()

        return [_serialize_attempt_question(attempt) for (attempt,) in rows]

    async def classroom_analytics(self, *, teacher_id: str, classroom_id: str) -> dict[str, Any]:
        tid = _parse_uuid(teacher_id)
        cid = _parse_uuid(classroom_id)
        classroom = await self.session.get(Classroom, cid)
        if classroom is None or classroom.teacher_id != tid:  # type: ignore
            raise AppError(status_code=404, code="not_found", message="Classroom not found")
        assert classroom is not None

        enroll_stmt = select(Enrollment.student_id).where(Enrollment.classroom_id == cid)
        student_ids = [row.student_id for row in (await self.session.execute(enroll_stmt)).all()]

        students: list[dict[str, Any]] = []
        for sid in student_ids:
            user = await self.session.get(User, sid)
            if user is None:
                continue
            assert user is not None
            snap_stmt = select(func.coalesce(func.avg(ProgressSnapshot.best_smartscore), 0)).where(ProgressSnapshot.user_id == sid)
            avg_best = round(float((await self.session.execute(snap_stmt)).scalar_one()))

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

        classroom_avg = round(sum(s["avg_best_smartscore"] for s in students) / max(1, len(students)))
        return {
            "classroom_id": str(cid),
            "title": classroom.title,  # type: ignore
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
            q_payload = attempt.question_payload or {}
            q_data = q_payload.get("data") or {}
            submitted = _as_dict(attempt.submitted_answer)
            submitted_qdata = _as_dict(submitted.get("questionData") or submitted.get("visualData"))
            q_seed = q_data.get("seed") or q_payload.get("seed") or submitted.get("seed") or submitted_qdata.get("seed")
            q_level = q_data.get("level") or q_payload.get("level") or submitted_qdata.get("level") or attempt.question_level

            sessions[key]["attempts"].append(
                {
                    "attempt_id": str(attempt.id),
                    "question_id": attempt.question_id,
                    "question_level": q_level,
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
                    "seed": q_seed,
                    "level": q_level,
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
        accuracy = round((int(total_correct) / max(1, int(total_attempts))) * 100)

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

    async def _teacher_student_ids(self, *, teacher_id: str) -> list[uuid.UUID]:
        tid = _parse_uuid(teacher_id)
        students = await list_teacher_scoped_students(self.session, teacher_id=tid)
        return [student.id for student in students]

    async def teacher_quickview_questions(self, *, teacher_id: str, limit: int = 200) -> list[dict[str, Any]]:
        student_ids = await self._teacher_student_ids(teacher_id=teacher_id)
        if not student_ids:
            return []

        attempts_stmt = (
            select(PracticeAttempt)
            .where(PracticeAttempt.user_id.in_(student_ids))
            .order_by(PracticeAttempt.answered_at.desc())
            .limit(limit)
        )
        q_rows = (await self.session.execute(attempts_stmt)).all()
        return [_serialize_attempt_question(attempt) for (attempt,) in q_rows]

    async def teacher_quickview(self, *, teacher_id: str, include_questions: bool = True) -> dict[str, Any]:
        student_ids = await self._teacher_student_ids(teacher_id=teacher_id)
        
        if not student_ids:
            return {
                "overview": {
                    "total_time_sec": 0,
                    "skills_practiced": 0,
                    "avg_accuracy_percent": 0,
                    "total_questions_answered": 0,
                    "total_skills_by_grade": {},
                },
                "skills": [],
                "all_questions": []
            }

        # 1. Overview stats
        time_stmt = select(func.coalesce(func.sum(PracticeSession.time_elapsed_sec), 0)).where(PracticeSession.user_id.in_(student_ids))
        total_time = int((await self.session.execute(time_stmt)).scalar_one())

        skills_stmt = select(func.count(func.distinct(PracticeSession.skill_id))).where(
            PracticeSession.user_id.in_(student_ids),
            PracticeSession.total_questions_answered > 0
        )
        skills_practiced = int((await self.session.execute(skills_stmt)).scalar_one())

        attempts_stmt = (
            select(
                func.count(PracticeAttempt.id),
                func.coalesce(func.sum(case((PracticeAttempt.is_correct.is_(True), 1), else_=0)), 0),
            )
            .select_from(PracticeAttempt)
            .where(PracticeAttempt.user_id.in_(student_ids))
        )
        total_attempts, correct_attempts = (await self.session.execute(attempts_stmt)).one()
        total_attempts = int(total_attempts)
        correct_attempts = int(correct_attempts)
        avg_accuracy = round((correct_attempts / max(1, total_attempts)) * 100)

        from app.models.catalog import Skill, Grade  # type: ignore
        skills_by_grade_stmt = (
            select(Grade.number, func.count(func.distinct(PracticeSession.skill_id)))
            .select_from(PracticeSession)
            .join(Skill, Skill.id == PracticeSession.skill_id)
            .join(Grade, Grade.id == Skill.grade_id)
            .where(PracticeSession.user_id.in_(student_ids))
            .group_by(Grade.number)
        )
        skills_by_grade_rows = (await self.session.execute(skills_by_grade_stmt)).all()
        total_skills_by_grade = {row[0]: row[1] for row in skills_by_grade_rows}

        overview = {
            "total_time_sec": total_time,
            "skills_practiced": skills_practiced,
            "avg_accuracy_percent": avg_accuracy,
            "total_questions_answered": total_attempts,
            "total_skills_by_grade": total_skills_by_grade,
        }

        # 2. Skills
        from app.models.topic import Topic  # type: ignore
        
        time_by_skill = (
            select(
                PracticeSession.skill_id.label("skill_id"),
                func.coalesce(func.sum(PracticeSession.active_time_seconds), 0).label("total_time_seconds"),
            )
            .where(PracticeSession.user_id.in_(student_ids))
            .group_by(PracticeSession.skill_id)
            .subquery()
        )

        stmt = (
            select(
                ProgressSnapshot.skill_id,
                func.max(ProgressSnapshot.best_smartscore).label("best_smartscore"),
                func.max(ProgressSnapshot.last_smartscore).label("last_smartscore"),
                func.max(ProgressSnapshot.last_practiced_at).label("last_practiced_at"),
                func.sum(ProgressSnapshot.total_questions).label("total_questions"),
                func.avg(ProgressSnapshot.accuracy_percent).label("accuracy_percent"),
                Skill.title.label('skill_name'),
                Skill.grade_id,
                Skill.topic_id,
                Grade.number.label('grade_number'),
                Topic.title.label('topic_title'),
                func.coalesce(time_by_skill.c.total_time_seconds, 0).label("total_time_seconds"),
            )
            .select_from(ProgressSnapshot)
            .join(Skill, Skill.id == ProgressSnapshot.skill_id)
            .join(Grade, Grade.id == Skill.grade_id)
            .outerjoin(Topic, Topic.id == Skill.topic_id)
            .outerjoin(time_by_skill, time_by_skill.c.skill_id == ProgressSnapshot.skill_id)
            .where(ProgressSnapshot.user_id.in_(student_ids))
            .group_by(
                ProgressSnapshot.skill_id,
                Skill.title,
                Skill.grade_id,
                Skill.topic_id,
                Grade.number,
                Topic.title,
                time_by_skill.c.total_time_seconds,
            )
            .order_by(func.max(ProgressSnapshot.last_practiced_at).desc().nullslast())
        )
        rows = (await self.session.execute(stmt)).all()

        skills_result = []
        for r in rows:
            skills_result.append({
                "skill_id": r.skill_id,
                "skill_name": r.skill_name,
                "grade_id": r.grade_id,
                "grade_number": r.grade_number,
                "topic_id": r.topic_id,
                "topic_title": r.topic_title,
                "best_smartscore": int(r.best_smartscore or 0),
                "last_smartscore": int(r.last_smartscore or 0),
                "last_practiced_at": r.last_practiced_at,
                "total_questions": int(r.total_questions or 0),
                "accuracy_percent": float(r.accuracy_percent or 0),
                "total_time_seconds": int(r.total_time_seconds or 0),
            })
            
        # 4. Per-student breakdown
        students_breakdown = []
        for sid in student_ids:
            user = await self.session.get(User, sid)
            if not user:
                continue

            # Student's total questions & time
            s_attempts_stmt = (
                select(
                    func.count(PracticeAttempt.id),
                    func.coalesce(func.sum(PracticeAttempt.time_spent_sec), 0),
                )
                .select_from(PracticeAttempt)
                .join(PracticeSession, PracticeSession.id == PracticeAttempt.session_id)
                .where(PracticeSession.user_id == sid)
            )
            s_total_q, s_total_time = (await self.session.execute(s_attempts_stmt)).one()
            s_total_q = int(s_total_q)
            s_total_time = int(s_total_time)

            # Student's skills from ProgressSnapshot
            s_skills_stmt = (
                select(
                    ProgressSnapshot.skill_id,
                    ProgressSnapshot.best_smartscore,
                    ProgressSnapshot.last_smartscore,
                    ProgressSnapshot.last_practiced_at,
                    ProgressSnapshot.total_questions,
                    Skill.title.label("skill_name"),
                    Skill.code.label("skill_code"),
                    Grade.number.label("grade_number"),
                    Grade.label.label("grade_label"),
                )
                .join(Skill, Skill.id == ProgressSnapshot.skill_id)
                .join(Grade, Grade.id == Skill.grade_id)
                .where(ProgressSnapshot.user_id == sid)
                .order_by(ProgressSnapshot.last_practiced_at.desc().nullslast())
            )
            s_skill_rows = (await self.session.execute(s_skills_stmt)).all()

            last_practiced = None
            mastered_count: int = 0
            proficient_count: int = 0
            practicing_count: int = 0
            s_skills_list = []
            for sr in s_skill_rows:
                if sr.last_practiced_at and (last_practiced is None or sr.last_practiced_at > last_practiced):
                    last_practiced = sr.last_practiced_at
                score = max(sr.best_smartscore or 0, sr.last_smartscore or 0)
                if score >= 90:
                    mastered_count += 1  # type: ignore
                elif score >= 70:
                    proficient_count += 1  # type: ignore
                elif score > 0:
                    practicing_count += 1  # type: ignore

                # Time for this skill
                sk_time_stmt = (
                    select(func.coalesce(func.sum(PracticeSession.active_time_seconds), 0))
                    .where(PracticeSession.user_id == sid, PracticeSession.skill_id == sr.skill_id)
                )
                sk_time = int((await self.session.execute(sk_time_stmt)).scalar_one())

                s_skills_list.append({
                    "skill_id": sr.skill_id,
                    "skill_name": sr.skill_name,
                    "skill_code": sr.skill_code,
                    "grade_number": sr.grade_number,
                    "grade_label": sr.grade_label if sr.grade_label else f"{sr.grade_number} сынып",
                    "total_questions": sr.total_questions or 0,
                    "total_time_seconds": sk_time,
                    "best_smartscore": sr.best_smartscore or 0,
                    "last_smartscore": sr.last_smartscore or 0,
                    "last_practiced_at": sr.last_practiced_at.isoformat() if sr.last_practiced_at else None,
                })

            students_breakdown.append({
                "student_id": str(sid),
                "full_name": user.full_name,
                "total_questions": s_total_q,
                "total_time_sec": s_total_time,
                "last_practiced_at": last_practiced,
                "mastered_count": mastered_count,
                "proficient_count": proficient_count,
                "practicing_count": practicing_count,
                "skills": s_skills_list,
            })

        return {
            "overview": overview,
            "skills": skills_result,
            "all_questions": await self.teacher_quickview_questions(teacher_id=teacher_id) if include_questions else [],
            "students_breakdown": students_breakdown,
        }


def _parse_uuid(value) -> uuid.UUID:
    try:
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
    except ValueError as e:
        raise AppError(status_code=400, code="validation_error", message="Invalid id") from e
