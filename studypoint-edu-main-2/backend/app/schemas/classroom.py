from __future__ import annotations

from pydantic import BaseModel, Field


class ClassroomCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    grade_id: int


class ClassroomResponse(BaseModel):
    id: str
    title: str
    grade_id: int


class ClassroomEnrollRequest(BaseModel):
    student_id: str

