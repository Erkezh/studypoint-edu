from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.enums import QuizQuestionOrder, QuizResultVisibility, QuizEndType


from app.schemas.practice import QuestionPublic

class QuizQuestionBase(BaseModel):
    question_id: int
    position: int = 0


class QuizQuestionCreate(QuizQuestionBase):
    seed: int | None = None


class QuizQuestionResponse(QuizQuestionBase):
    id: uuid.UUID
    seed: int | None = None
    question: QuestionPublic | None = None

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    question_order: QuizQuestionOrder = QuizQuestionOrder.FIXED
    result_visibility: QuizResultVisibility = QuizResultVisibility.ALWAYS
    end_type: QuizEndType = QuizEndType.MANUAL


class QuizCreateRequest(QuizBase):
    questions: list[QuizQuestionCreate]


class QuizResponse(QuizBase):
    id: uuid.UUID
    teacher_id: uuid.UUID
    created_at: datetime
    questions: list[QuizQuestionResponse]

    class Config:
        from_attributes = True


class QuizAssignmentBase(BaseModel):
    quiz_id: uuid.UUID
    classroom_id: uuid.UUID | None = None
    student_id: uuid.UUID | None = None
    due_at: datetime | None = None
    end_at: datetime | None = None


class QuizAssignmentCreate(QuizAssignmentBase):
    pass


class QuizAssignmentResponse(QuizAssignmentBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class StudentQuizAssignmentResponse(BaseModel):
    id: uuid.UUID
    quiz_id: uuid.UUID
    quiz: QuizResponse
    due_at: datetime | None = None
    end_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True
