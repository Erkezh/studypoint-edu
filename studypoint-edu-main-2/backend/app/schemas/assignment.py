from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class AssignmentCreateRequest(BaseModel):
    classroom_id: str
    skill_id: int
    due_at: datetime | None = None
    target_smartscore: int = Field(default=80, examples=[70, 80, 90, 100])


class AssignmentResponse(BaseModel):
    id: str
    classroom_id: str
    skill_id: int
    due_at: datetime | None
    target_smartscore: int | None = None


class AssignmentStatusResponse(BaseModel):
    assignment_id: str
    student_id: str
    status: str
    best_smartscore: int
    last_smartscore: int
    questions_answered: int
    time_spent_seconds: int
    completed_at: datetime | None
    last_activity_at: datetime | None


class StudentAssignmentResponse(BaseModel):
    assignment: AssignmentResponse
    status: AssignmentStatusResponse
