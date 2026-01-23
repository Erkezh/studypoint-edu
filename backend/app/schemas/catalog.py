from __future__ import annotations

from pydantic import BaseModel, Field


class SubjectResponse(BaseModel):
    id: int
    slug: str
    title: str


class GradeResponse(BaseModel):
    id: int
    number: int = Field(examples=[-1, 0, 1, 12])
    title: str


class SkillListItem(BaseModel):
    id: int
    subject_id: int
    grade_id: int
    code: str
    title: str
    difficulty: int
    tags: list[str]


class SkillDetailResponse(SkillListItem):
    description: str
    example_url: str | None = None
    video_url: str | None = None
    is_published: bool

