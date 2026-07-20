from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.db.session import get_db_session
from app.models.quiz import Quiz, QuizQuestion, QuizAssignment
from app.schemas.quiz import QuizCreateRequest, QuizAssignmentCreate
from app.schemas.quiz import StudentQuizAssignmentResponse


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
            ended_result_visibility=req.ended_result_visibility,
            end_type=req.end_type
        )
        self.session.add(quiz)
        await self.session.flush()

        for q_req in req.questions:
            quiz_q = QuizQuestion(
                quiz_id=quiz.id,
                question_id=q_req.question_id,
                position=q_req.position,
                seed=q_req.seed
            )
            self.session.add(quiz_q)
            
        await self.session.flush()

        # Handle assignments if not draft
        if not req.is_draft:
            student_ids = req.student_ids
            if not student_ids:
                from app.services.teacher_scope import list_teacher_scoped_students
                scoped = await list_teacher_scoped_students(self.session, teacher_id=teacher_uuid)
                student_ids = [s.id for s in scoped]

            for student_id in student_ids:
                assignment = QuizAssignment(
                    quiz_id=quiz.id,
                    classroom_id=req.classroom_id,
                    student_id=student_id,
                    end_at=req.end_at
                )
                self.session.add(assignment)
            await self.session.flush()

            # Trigger real-time notifications for assigned students
            try:
                from app.models.notification import Notification
                for student_id in student_ids:
                    self.session.add(
                        Notification(
                            user_id=student_id,
                            title="Жаңа квиз!",
                            content=f"Мұғалім жаңа квиз жариялады: '{quiz.name}'.",
                            is_read=False,
                        )
                    )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to generate quiz notifications in create_quiz: {e}", exc_info=True)
            await self.session.flush()
        
        # Load questions for response
        stmt = select(Quiz).where(Quiz.id == quiz.id).options(
            selectinload(Quiz.questions).joinedload(QuizQuestion.question),
            selectinload(Quiz.assignments)
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
        quiz.ended_result_visibility = req.ended_result_visibility
        quiz.end_type = req.end_type

        # Remove old questions
        del_stmt = select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_uuid)
        result = await self.session.execute(del_stmt)
        for old_q in result.scalars().all():
            await self.session.delete(old_q)

        # Remove old assignments to allow updating selected students
        del_assign_stmt = select(QuizAssignment).where(QuizAssignment.quiz_id == quiz_uuid)
        assign_result = await self.session.execute(del_assign_stmt)
        for old_assign in assign_result.scalars().all():
            await self.session.delete(old_assign)
            
        await self.session.flush()

        for q_req in req.questions:
            quiz_q = QuizQuestion(
                quiz_id=quiz.id,
                question_id=q_req.question_id,
                position=q_req.position,
                seed=q_req.seed
            )
            self.session.add(quiz_q)

        await self.session.flush()

        # Handle assignments if not draft
        if not req.is_draft:
            student_ids = req.student_ids
            if not student_ids:
                from app.services.teacher_scope import list_teacher_scoped_students
                scoped = await list_teacher_scoped_students(self.session, teacher_id=teacher_uuid)
                student_ids = [s.id for s in scoped]

            for student_id in student_ids:
                assignment = QuizAssignment(
                    quiz_id=quiz.id,
                    classroom_id=req.classroom_id,
                    student_id=student_id,
                    end_at=req.end_at
                )
                self.session.add(assignment)
            await self.session.flush()

            # Trigger real-time notifications for assigned students
            try:
                from app.models.notification import Notification
                for student_id in student_ids:
                    self.session.add(
                        Notification(
                            user_id=student_id,
                            title="Жаңа квиз!",
                            content=f"Мұғалім жаңа квиз жариялады: '{quiz.name}'.",
                            is_read=False,
                        )
                    )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to generate quiz notifications in update_quiz: {e}", exc_info=True)
            await self.session.flush()

        # Reload with questions
        stmt = select(Quiz).where(Quiz.id == quiz.id).options(
            selectinload(Quiz.questions).joinedload(QuizQuestion.question),
            selectinload(Quiz.assignments)
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def list_quizzes(self, teacher_id: uuid.UUID | str) -> Sequence[Quiz]:
        teacher_uuid = uuid.UUID(str(teacher_id))
        stmt = (
            select(Quiz)
            .where(Quiz.teacher_id == teacher_uuid)
            .options(
                selectinload(Quiz.questions).joinedload(QuizQuestion.question),
                selectinload(Quiz.assignments)
            )
            .order_by(Quiz.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all_quizzes(self) -> Sequence[Quiz]:
        """Return all quizzes from all teachers (for student view)."""
        stmt = (
            select(Quiz)
            .options(
                selectinload(Quiz.questions).joinedload(QuizQuestion.question),
                selectinload(Quiz.assignments)
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
        # If student_id is set, assign only to them
        if req.student_id:
            student_ids = [req.student_id]
        else:
            student_ids = []
            if req.classroom_id:
                from app.models.classroom import Enrollment
                classroom_stmt = select(Enrollment.student_id).where(Enrollment.classroom_id == req.classroom_id)
                classroom_res = await self.session.execute(classroom_stmt)
                student_ids = list(classroom_res.scalars().all())
            else:
                quiz = await self.get_quiz(req.quiz_id)
                teacher_id = quiz.teacher_id if quiz else None
                if teacher_id:
                    from app.services.teacher_scope import list_teacher_scoped_students
                    scoped = await list_teacher_scoped_students(self.session, teacher_id=teacher_id)
                    student_ids = [s.id for s in scoped]
                else:
                    from app.models.user import User
                    from app.models.enums import UserRole
                    student_stmt = select(User.id).where(User.role == UserRole.STUDENT)
                    student_res = await self.session.execute(student_stmt)
                    student_ids = list(student_res.scalars().all())
                
        first_assignment = None
        for s_id in student_ids:
            # Delete any existing assignment for this student and quiz to avoid duplicate key issues
            del_stmt = select(QuizAssignment).where(QuizAssignment.quiz_id == req.quiz_id, QuizAssignment.student_id == s_id)
            del_res = await self.session.execute(del_stmt)
            for old_a in del_res.scalars().all():
                await self.session.delete(old_a)
                
            assignment = QuizAssignment(
                quiz_id=req.quiz_id,
                classroom_id=req.classroom_id,
                student_id=s_id,
                due_at=req.due_at,
                end_at=req.end_at
            )
            self.session.add(assignment)
            if not first_assignment:
                first_assignment = assignment
                
        # Trigger real-time notifications for assigned students
        try:
            from app.models.notification import Notification
            quiz_stmt = select(Quiz).where(Quiz.id == req.quiz_id)
            quiz_result = await self.session.execute(quiz_stmt)
            quiz = quiz_result.scalar_one_or_none()
            quiz_name = quiz.name if quiz else "Квиз"
            
            for s_id in student_ids:
                self.session.add(
                    Notification(
                        user_id=s_id,
                        title="Жаңа квиз!",
                        content=f"Мұғалім жаңа квиз жариялады: '{quiz_name}'.",
                        is_read=False,
                    )
                )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to generate quiz notifications: {e}", exc_info=True)

        await self.session.flush()
        if first_assignment:
            await self.session.refresh(first_assignment)
            return first_assignment
        else:
            fallback = QuizAssignment(
                quiz_id=req.quiz_id,
                classroom_id=req.classroom_id,
                student_id=req.student_id,
                due_at=req.due_at,
                end_at=req.end_at
            )
            self.session.add(fallback)
            await self.session.flush()
            await self.session.refresh(fallback)
            return fallback

    async def list_assigned_quizzes(self, student_id: uuid.UUID | str) -> Sequence[QuizAssignment]:
        student_uuid = uuid.UUID(str(student_id))
        stmt = (
            select(QuizAssignment)
            .where(QuizAssignment.student_id == student_uuid)
            .options(
                joinedload(QuizAssignment.quiz).options(
                    selectinload(Quiz.questions).joinedload(QuizQuestion.question),
                    selectinload(Quiz.assignments)
                )
            )
            .order_by(QuizAssignment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
        
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

    async def end_quiz_assignment(self, assignment_id: uuid.UUID | str) -> QuizAssignment | None:
        from datetime import datetime, timezone
        assignment_uuid = uuid.UUID(str(assignment_id))
        stmt = select(QuizAssignment).where(QuizAssignment.id == assignment_uuid)
        result = await self.session.execute(stmt)
        assignment = result.scalar_one_or_none()
        
        if not assignment:
            return None
            
        assignment.end_at = datetime.now(timezone.utc)
        await self.session.flush()
        return assignment

    async def submit_quiz_assignment(
        self,
        student_id: uuid.UUID | str,
        assignment_id: uuid.UUID | str,
        score: int, # unused now, but kept for interface signature compatibility
        time_spent_seconds: int,
        question_results: dict | list
    ) -> QuizAssignment | None:
        student_uuid = uuid.UUID(str(student_id))
        assignment_uuid = uuid.UUID(str(assignment_id))
        
        stmt = select(QuizAssignment).where(
            QuizAssignment.id == assignment_uuid,
            QuizAssignment.student_id == student_uuid
        )
        result = await self.session.execute(stmt)
        assignment = result.scalar_one_or_none()
        
        if not assignment:
            return None

        # Load the quiz questions to grade them
        from app.models.quiz import Quiz, QuizQuestion
        from app.services.practice_service import _is_correct
        
        quiz_stmt = (
            select(Quiz)
            .where(Quiz.id == assignment.quiz_id)
            .options(
                selectinload(Quiz.questions).joinedload(QuizQuestion.question)
            )
        )
        quiz_res = await self.session.execute(quiz_stmt)
        quiz = quiz_res.scalar_one_or_none()
        
        if not quiz:
            return None

        # Map submitted answers by question_id (as strings for easy comparison)
        answers_map = {}
        # question_results is list of dict: [{"question_id": "...", "submitted_answer": "..."}]
        if isinstance(question_results, list):
            for r in question_results:
                if isinstance(r, dict):
                    q_id = str(r.get("question_id") or "")
                    sub_ans = r.get("submitted_answer")
                    answers_map[q_id] = sub_ans

        correct_count = 0
        total_count = len(quiz.questions)
        graded_results = {}

        # Sort questions by position to maintain the same ordering
        sorted_qs = sorted(quiz.questions, key=lambda x: x.position)
        for qq in sorted_qs:
            q = qq.question
            if not q:
                continue
                
            q_id_str = str(qq.id)
            submitted_ans = answers_map.get(q_id_str)

            # Normalize if submitted_ans is a dict
            if isinstance(submitted_ans, dict) and q.type.value not in ("PLUGIN", "INTERACTIVE"):
                submitted_ans = (
                    submitted_ans.get("id")
                    or submitted_ans.get("value") 
                    or submitted_ans.get("label") 
                    or submitted_ans.get("text") 
                    or submitted_ans
                )

            submitted_payload = {}
            if q.type.value == "MCQ":
                submitted_payload = {"choice": submitted_ans}
            elif q.type.value == "NUMERIC":
                submitted_payload = {"value": submitted_ans}
            elif q.type.value == "TEXT":
                submitted_payload = {"text": submitted_ans}
            else:
                if isinstance(submitted_ans, dict):
                    submitted_payload = submitted_ans
                else:
                    submitted_payload = {"answer": submitted_ans, "value": submitted_ans, "text": submitted_ans, "choice": submitted_ans}
                    
            is_correct = False
            if q.type.value in ("PLUGIN", "INTERACTIVE"):
                if isinstance(submitted_ans, dict):
                    is_correct_val = (
                        submitted_ans.get("isCorrect") 
                        if submitted_ans.get("isCorrect") is not None 
                        else submitted_ans.get("is_correct") 
                        if submitted_ans.get("is_correct") is not None 
                        else submitted_ans.get("correct")
                    )
                    if isinstance(is_correct_val, str):
                        is_correct = is_correct_val.lower() in ("true", "1", "yes")
                    elif is_correct_val is not None:
                        is_correct = bool(is_correct_val)
                
                # Fallback to backend plugin service evaluation if not resolved/correct in the payload
                if not is_correct:
                    try:
                        from app.plugins.service import PluginService
                        plugin_id = (q.data or {}).get("plugin_id")
                        if plugin_id:
                            plugin_svc = PluginService(self.session)
                            result = await plugin_svc.evaluate_answer(
                                plugin_id=plugin_id,
                                task_id=str(assignment_uuid),
                                user_answer=submitted_payload,
                            )
                            if isinstance(result, dict):
                                is_correct_val = (
                                    result.get("correct") 
                                    if result.get("correct") is not None 
                                    else result.get("is_correct") 
                                    if result.get("is_correct") is not None 
                                    else result.get("isCorrect")
                                )
                                if isinstance(is_correct_val, str):
                                    is_correct = is_correct_val.lower() in ("true", "1", "yes")
                                elif is_correct_val is not None:
                                    is_correct = bool(is_correct_val)
                    except Exception as e:
                        import logging
                        logging.getLogger(__name__).error(f"Failed to evaluate plugin answer in quiz: {e}", exc_info=True)
            else:
                is_correct = _is_correct(q.type, q.data, q.correct_answer, submitted_payload)

            if is_correct:
                correct_count += 1
            graded_results[q_id_str] = {
                "correct": is_correct,
                "submitted_answer": submitted_payload if q.type.value in ("PLUGIN", "INTERACTIVE") else submitted_ans,
                "correct_answer": q.correct_answer,
                "question": submitted_payload.get("question") if isinstance(submitted_payload, dict) else None
            }

        computed_score = 0
        if total_count > 0:
            computed_score = round((correct_count / total_count) * 100)

        assignment.completed_at = datetime.now(timezone.utc)
        assignment.score = computed_score
        assignment.time_spent_seconds = time_spent_seconds
        assignment.question_results = graded_results
        
        await self.session.commit()
        return assignment

    async def start_quiz_assignment(self, student_id: uuid.UUID | str, assignment_id: uuid.UUID | str) -> QuizAssignment | None:
        student_uuid = uuid.UUID(str(student_id))
        assignment_uuid = uuid.UUID(str(assignment_id))
        stmt = select(QuizAssignment).where(
            QuizAssignment.id == assignment_uuid,
            QuizAssignment.student_id == student_uuid
        )
        res = await self.session.execute(stmt)
        assignment = res.scalar_one_or_none()
        if not assignment:
            return None
        if not assignment.started_at:
            assignment.started_at = datetime.now(timezone.utc)
            await self.session.commit()
        return assignment
