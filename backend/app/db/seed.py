from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import close_engine, get_sessionmaker, init_engine
from app.models.assignment import Assignment, AssignmentStatusRow
from app.models.catalog import Grade, Skill, Subject
from app.models.classroom import Classroom, Enrollment
from app.models.enums import AssignmentStatus, QuestionType, SubscriptionPlan, UserRole
from app.models.profile import StudentProfile
from app.models.question import Question
from app.models.subscription import Subscription
from app.models.user import User
from app.core.config import settings


async def _ensure_subjects(session: AsyncSession) -> None:
    existing = (await session.execute(select(Subject.id).limit(1))).scalar_one_or_none()
    if existing is not None:
        return

    subjects = [
        Subject(id=1, slug="math", title="Math"),
        Subject(id=2, slug="language-arts", title="Language Arts"),
        Subject(id=3, slug="science", title="Science"),
        Subject(id=4, slug="social-studies", title="Social Studies"),
        Subject(id=5, slug="spanish", title="Spanish"),
    ]
    session.add_all(subjects)


async def _ensure_grades(session: AsyncSession) -> None:
    existing = (await session.execute(select(Grade.id).limit(1))).scalar_one_or_none()
    if existing is not None:
        return

    grades: list[Grade] = [
        Grade(id=1, number=-1, title="Pre-K"),
        Grade(id=2, number=0, title="K"),
    ]
    next_id = 3
    for n in range(1, 13):
        grades.append(Grade(id=next_id, number=n, title=str(n)))
        next_id += 1
    session.add_all(grades)


async def _ensure_demo_content(session: AsyncSession) -> None:
    existing = (await session.execute(select(Skill.id).limit(1))).scalar_one_or_none()
    if existing is not None:
        return

    # Grade 5 Math: id=7 because Pre-K(-1)=1, K(0)=2, 1..5 => ids 3..7.
    grade5_id = 7
    math_id = 1

    skill1 = Skill(
        id=1,
        subject_id=math_id,
        grade_id=grade5_id,
        code="A.1",
        title="Multiply whole numbers",
        description="Multiply two whole numbers.",
        tags=["multiplication"],
        difficulty=2,
        is_published=True,
    )
    skill2 = Skill(
        id=2,
        subject_id=math_id,
        grade_id=grade5_id,
        code="A.2",
        title="Divide whole numbers",
        description="Divide a whole number by a whole number.",
        tags=["division"],
        difficulty=2,
        is_published=True,
    )
    session.add_all([skill1, skill2])

    q1 = Question(
        id=1,
        skill_id=1,
        type=QuestionType.MCQ,
        prompt="What is 7 × 8?",
        data={"choices": [{"id": "A", "text": "54"}, {"id": "B", "text": "56"}, {"id": "C", "text": "64"}]},
        correct_answer={"choice": "B"},
        explanation="7 × 8 = 56.",
        level=2,
    )
    q2 = Question(
        id=2,
        skill_id=1,
        type=QuestionType.NUMERIC,
        prompt="Compute 12 × 9.",
        data={"min": 0, "max": 1000},
        correct_answer={"value": 108},
        explanation="12 × 9 = 108.",
        level=2,
    )
    q3 = Question(
        id=3,
        skill_id=2,
        type=QuestionType.MCQ,
        prompt="What is 72 ÷ 9?",
        data={"choices": [{"id": "A", "text": "8"}, {"id": "B", "text": "9"}, {"id": "C", "text": "7"}]},
        correct_answer={"choice": "A"},
        explanation="72 ÷ 9 = 8.",
        level=2,
    )
    session.add_all([q1, q2, q3])


async def _ensure_demo_users(session: AsyncSession) -> None:
    existing = (await session.execute(select(User).where(User.email == "admin@example.com"))).scalar_one_or_none()
    if existing is not None:
        return

    admin = User(
        email="admin@example.com",
        password_hash=hash_password("Password123!"),
        full_name="Admin",
        role=UserRole.ADMIN,
        is_active=True,
    )
    teacher = User(
        email="teacher@example.com",
        password_hash=hash_password("Password123!"),
        full_name="Teacher",
        role=UserRole.TEACHER,
        is_active=True,
    )
    student = User(
        email="student@example.com",
        password_hash=hash_password("Password123!"),
        full_name="Student",
        role=UserRole.STUDENT,
        is_active=True,
    )
    session.add_all([admin, teacher, student])
    await session.flush()

    session.add(StudentProfile(user_id=student.id, grade_level=5, school="Demo School"))
    session.add(Subscription(user_id=student.id, plan=SubscriptionPlan.FREE, is_active=True))

    classroom = Classroom(teacher_id=teacher.id, title="Demo Grade 5", grade_id=7)
    session.add(classroom)
    await session.flush()
    session.add(Enrollment(classroom_id=classroom.id, student_id=student.id, enrolled_at=datetime.now(timezone.utc)))

    assignment = Assignment(classroom_id=classroom.id, skill_id=1, due_at=None)
    session.add(assignment)
    await session.flush()
    session.add(
        AssignmentStatusRow(
            assignment_id=assignment.id,
            student_id=student.id,
            status=AssignmentStatus.NOT_STARTED,
        )
    )


async def _reset_sequences(session: AsyncSession) -> None:
    # We insert fixed IDs in seed data; ensure sequences advance for future inserts.
    for table in ["subjects", "grades", "skills", "questions"]:
        await session.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1), true);"
            )
        )


async def seed() -> None:
    init_engine(settings.database_url)
    sessionmaker = get_sessionmaker()

    try:
        async with sessionmaker() as session:
            async with session.begin():
                await _ensure_subjects(session)
                await _ensure_grades(session)
                await _ensure_demo_content(session)
                await _ensure_demo_users(session)
                await _reset_sequences(session)
    finally:
        await close_engine()


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
