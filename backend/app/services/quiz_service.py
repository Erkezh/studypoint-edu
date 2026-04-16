from __future__ import annotations

import uuid
from typing import Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.db.session import get_db_session
from app.models.quiz import Quiz, QuizQuestion, QuizAssignment
from app.schemas.quiz import QuizCreateRequest, QuizAssignmentCreate


class QuizService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create_quiz(self, teacher_id: uuid.UUID | str, req: QuizCreateRequest) -> Quiz:
        teacher_uuid = uuid.UUID(str(teacher_id))
        
        quiz = Quiz(
            name=req.name,
            teacher_id=teacher_uuid,
            question_order=req.question_order,
            result_visibility=req.result_visibility,
            end_type=req.end_type
        )
        self.session.add(quiz)
        await self.session.flush()

        for q_req in req.questions:
            quiz_q = QuizQuestion(
                quiz_id=quiz.id,
                question_id=q_req.question_id,
                position=q_req.position
            )
            self.session.add(quiz_q)
            
        await self.session.flush()
        await self.session.refresh(quiz)
        
        # Load questions for response
        stmt = select(Quiz).where(Quiz.id == quiz.id).options(
            selectinload(Quiz.questions).joinedload(QuizQuestion.question)
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def update_quiz(self, teacher_id: uuid.UUID | str, quiz_id: uuid.UUID | str, req: QuizCreateRequest) -> Quiz:
        teacher_uuid = uuid.UUID(str(teacher_id))
        quiz_uuid = uuid.UUID(str(quiz_id))

        stmt = select(Quiz).where(Quiz.id == quiz_uuid, Quiz.teacher_id == teacher_uuid)
        result = await self.session.execute(stmt)
        quiz = result.scalar_one_or_none()

        if not quiz:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Quiz not found")

        quiz.name = req.name
        quiz.question_order = req.question_order
        quiz.result_visibility = req.result_visibility
        quiz.end_type = req.end_type

        # Remove old questions
        del_stmt = select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_uuid)
        result = await self.session.execute(del_stmt)
        for old_q in result.scalars().all():
            await self.session.delete(old_q)
            
        await self.session.flush()

        for q_req in req.questions:
            quiz_q = QuizQuestion(
                quiz_id=quiz.id,
                question_id=q_req.question_id,
                position=q_req.position
            )
            self.session.add(quiz_q)

        await self.session.flush()

        # Reload with questions
        stmt = select(Quiz).where(Quiz.id == quiz.id).options(
            selectinload(Quiz.questions).joinedload(QuizQuestion.question)
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def list_quizzes(self, teacher_id: uuid.UUID | str) -> Sequence[Quiz]:
        teacher_uuid = uuid.UUID(str(teacher_id))
        stmt = (
            select(Quiz)
            .where(Quiz.teacher_id == teacher_uuid)
            .options(
                selectinload(Quiz.questions).joinedload(QuizQuestion.question)
            )
            .order_by(Quiz.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_quiz(self, quiz_id: uuid.UUID | str) -> Quiz | None:
        quiz_uuid = uuid.UUID(str(quiz_id))
        stmt = (
            select(Quiz)
            .where(Quiz.id == quiz_uuid)
            .options(
                selectinload(Quiz.questions).joinedload(QuizQuestion.question)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def assign_quiz(self, req: QuizAssignmentCreate) -> QuizAssignment:
        assignment = QuizAssignment(
            quiz_id=req.quiz_id,
            classroom_id=req.classroom_id,
            student_id=req.student_id,
            due_at=req.due_at,
            end_at=req.end_at
        )
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment
        
    async def delete_quiz(self, teacher_id: uuid.UUID | str, quiz_id: uuid.UUID | str) -> bool:
        teacher_uuid = uuid.UUID(str(teacher_id))
        quiz_uuid = uuid.UUID(str(quiz_id))
        
        stmt = select(Quiz).where(Quiz.id == quiz_uuid, Quiz.teacher_id == teacher_uuid)
        result = await self.session.execute(stmt)
        quiz = result.scalar_one_or_none()
        
        if not quiz:
            return False
            
        await self.session.delete(quiz)
        await self.session.flush()
        return True
