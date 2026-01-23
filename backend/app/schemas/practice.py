from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.models.enums import QuestionType


class QuestionPublic(BaseModel):
    id: int
    skill_id: int
    type: QuestionType
    prompt: str
    data: dict[str, Any] = Field(default_factory=dict)
    level: int


class PracticeSessionCreateRequest(BaseModel):
    skill_id: int = Field(examples=[1])


class PracticeSessionResponse(BaseModel):
    id: str
    skill_id: int
    started_at: datetime
    finished_at: datetime | None
    questions_answered: int
    correct_count: int
    wrong_count: int
    smartscore: int
    time_elapsed_sec: int
    state: dict[str, Any]
    current_question: QuestionPublic | None = None

    # IXL-like fields (added, backwards compatible)
    current_smartscore: int | None = None
    best_smartscore: int | None = None
    total_questions_answered: int | None = None
    total_correct: int | None = None
    total_incorrect: int | None = None
    current_streak_correct: int | None = None
    max_streak_correct: int | None = None
    current_zone: str | None = None
    last_question_id: int | None = None
    last_activity_at: datetime | None = None
    active_time_seconds: int | None = None
    inactivity_threshold_seconds: int | None = None


class PracticeSubmitRequest(BaseModel):
    question_id: int | str  # Для генераторов может быть строкой (например, "generated_0")
    submitted_answer: dict[str, Any]
    time_spent_sec: int = Field(ge=0, le=3600)


class PracticeSubmitResponse(BaseModel):
    is_correct: bool
    explanation: str | None = None
    session: PracticeSessionResponse
    next_question: QuestionPublic | None = None
    finished: bool


class PracticeHeartbeatRequest(BaseModel):
    client_ts: datetime | None = None
    is_active: bool = True
    focus: bool = True
    interaction: bool = True
