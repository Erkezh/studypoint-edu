from __future__ import annotations

import uuid
from datetime import date

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.assignment import Assignment, AssignmentStatusRow
from app.models.awards import AwardEvent
from app.models.catalog import Skill
from app.models.classroom import Classroom, Enrollment
from app.models.practice import PracticeAttempt, PracticeSession
from app.models.user import User
from app.utils.pdf import build_assignment_report_pdf, build_certificate_pdf, build_practice_session_report_pdf
from app.utils.time import utc_now


class ReportService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def practice_session_pdf(
        self,
        *,
        requester_id: str,
        requester_role: str,
        session_id: str,
        paper: str | None,
    ) -> bytes:
        sid = _parse_uuid(session_id)
        rid = _parse_uuid(requester_id)
        ps = await self.session.get(PracticeSession, sid)
        if ps is None:
            raise AppError(status_code=404, code="not_found", message="Session not found")

        if requester_role not in {"ADMIN", "TEACHER"} and ps.user_id != rid:
            raise AppError(status_code=403, code="forbidden", message="Insufficient permissions")

        if requester_role == "TEACHER" and ps.user_id != rid:
            stmt = (
                select(func.count())
                .select_from(Enrollment)
                .join(Classroom, Classroom.id == Enrollment.classroom_id)
                .where(Classroom.teacher_id == rid, Enrollment.student_id == ps.user_id)
            )
            if int((await self.session.execute(stmt)).scalar_one()) == 0:
                raise AppError(status_code=403, code="forbidden", message="Student not in your classrooms")

        user = await self.session.get(User, ps.user_id)
        skill = await self.session.get(Skill, ps.skill_id)
        if user is None or skill is None:
            raise AppError(status_code=404, code="not_found", message="Report source not found")

        attempts_stmt = (
            select(PracticeAttempt)
            .where(PracticeAttempt.session_id == ps.id)
            .order_by(PracticeAttempt.answered_at.asc())
        )
        attempts = list((await self.session.execute(attempts_stmt)).scalars().all())

        header = {
            "student": user.full_name,
            "skill": f"{skill.code} — {skill.title}",
            "date": ps.started_at.date().isoformat(),
            "current_smartscore": ps.current_smartscore,
            "best_smartscore": ps.best_smartscore,
            "questions_answered": ps.total_questions_answered,
            "correct": ps.total_correct,
            "incorrect": ps.total_incorrect,
            "active_time_seconds": ps.active_time_seconds,
        }
        rows = []
        for a in attempts:
            qp = a.question_payload or {}
            rows.append(
                {
                    "answered_at": a.answered_at.isoformat(),
                    "question": qp.get("prompt") or "",
                    "submitted_answer": _compact_json(a.submitted_answer),
                    "correct_answer": _compact_json(qp.get("correct_answer")),
                    "is_correct": bool(a.is_correct),
                    "time_spent_sec": int(a.time_spent_sec or 0),
                    "smartscore_before": int(a.smartscore_before or 0),
                    "smartscore_after": int(a.smartscore_after or 0),
                }
            )

        return build_practice_session_report_pdf(paper=paper, header=header, rows=rows)

    async def assignment_pdf(
        self,
        *,
        requester_id: str,
        requester_role: str,
        assignment_id: str,
        paper: str | None,
    ) -> bytes:
        rid = _parse_uuid(requester_id)
        aid = _parse_uuid(assignment_id)
        assignment = await self.session.get(Assignment, aid)
        if assignment is None:
            raise AppError(status_code=404, code="not_found", message="Assignment not found")

        if requester_role not in {"ADMIN", "TEACHER"}:
            raise AppError(status_code=403, code="forbidden", message="Insufficient permissions")

        if requester_role == "TEACHER":
            classroom = await self.session.get(Classroom, assignment.classroom_id)
            if classroom is None or classroom.teacher_id != rid:
                raise AppError(status_code=403, code="forbidden", message="Insufficient permissions")

        skill = await self.session.get(Skill, assignment.skill_id)
        if skill is None:
            raise AppError(status_code=404, code="not_found", message="Skill not found")

        stmt = (
            select(User, AssignmentStatusRow)
            .join(AssignmentStatusRow, AssignmentStatusRow.student_id == User.id)
            .where(AssignmentStatusRow.assignment_id == assignment.id)
            .order_by(User.full_name.asc())
        )
        rows = (await self.session.execute(stmt)).all()
        grid_rows = []
        completed = 0
        in_progress = 0
        not_started = 0
        for u, s in rows:
            status = s.status.value if hasattr(s.status, "value") else str(s.status)
            if status == "COMPLETED":
                completed += 1
            elif status == "IN_PROGRESS":
                in_progress += 1
            else:
                not_started += 1
            grid_rows.append(
                {
                    "student": u.full_name,
                    "status": status,
                    "best_smartscore": s.best_smartscore,
                    "last_smartscore": s.last_smartscore,
                    "questions_answered": s.questions_answered,
                    "time_spent_seconds": getattr(s, "time_spent_seconds", 0),
                    "last_activity_at": (getattr(s, "last_activity_at", None).isoformat() if getattr(s, "last_activity_at", None) else None),
                }
            )

        header = {
            "assignment_id": str(assignment.id),
            "skill": f"{skill.code} — {skill.title}",
            "target_smartscore": assignment.target_smartscore,
            "due_at": assignment.due_at.isoformat() if assignment.due_at else "",
            "summary": f"Completed {completed} / In progress {in_progress} / Not started {not_started}",
        }
        return build_assignment_report_pdf(paper=paper, header=header, rows=grid_rows)

    async def certificate_pdf(
        self,
        *,
        requester_id: str,
        requester_role: str,
        student_id: str | None,
        skill_id: int,
        type: str,
        paper: str | None,
        date_str: str | None,
        awarded_by: str | None,
        related_session_id: str | None,
    ) -> bytes:
        rid = _parse_uuid(requester_id)
        sid = _parse_uuid(student_id) if student_id else rid

        if sid != rid and requester_role not in {"TEACHER", "ADMIN"}:
            raise AppError(status_code=403, code="forbidden", message="Insufficient permissions")

        user = await self.session.get(User, sid)
        skill = await self.session.get(Skill, skill_id)
        if user is None or skill is None:
            raise AppError(status_code=404, code="not_found", message="Not found")

        if type not in {"EXCELLENCE", "MASTERY"}:
            raise AppError(status_code=400, code="validation_error", message="type must be EXCELLENCE or MASTERY")

        title = "Certificate of Excellence" if type == "EXCELLENCE" else "Certificate of Mastery"
        d = date_str or date.today().isoformat()

        # Store an award event for audit/printing history.
        rel = _parse_uuid(related_session_id) if related_session_id else None
        self.session.add(AwardEvent(user_id=sid, skill_id=skill_id, type=type, issued_at=utc_now(), related_session_id=rel))
        await self.session.flush()

        return build_certificate_pdf(
            paper=paper,
            title=title,
            student_name=user.full_name,
            skill_name=f"{skill.code} — {skill.title}",
            date_str=d,
            awarded_by=awarded_by,
        )


def _parse_uuid(value: str | None) -> uuid.UUID:
    if not value:
        raise AppError(status_code=400, code="validation_error", message="Invalid id")
    try:
        return uuid.UUID(str(value))
    except ValueError as e:
        raise AppError(status_code=400, code="validation_error", message="Invalid id") from e


def _compact_json(obj) -> str:
    if obj is None:
        return ""
    try:
        import json

        return json.dumps(obj, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(obj)

