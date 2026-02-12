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


class TopicResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str = ""
    icon: str | None = None
    order: int = 0
    is_published: bool = True


class SkillListItem(BaseModel):
    id: int
    subject_id: int
    grade_id: int
    topic_id: int | None = None
    topic_title: str | None = None
    code: str
    title: str
    difficulty: int
    tags: list[str]


class SkillDetailResponse(SkillListItem):
    description: str
    example_url: str | None = None
    video_url: str | None = None
    is_published: bool



class SkillUpdate(BaseModel):
    grade_id: int | None = None
    topic_id: int | None = None
    code: str | None = None
    title: str | None = None
