from __future__ import annotations

from pydantic import BaseModel, Field


class TeacherCreateStudentRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    grade_id: int
    classroom_id: str | None = None


class TeacherCreateStudentResponse(BaseModel):
    id: str
    full_name: str
    username: str
    password: str
