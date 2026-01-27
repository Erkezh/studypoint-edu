from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import QuestionType


class SubjectCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=128)


class SubjectUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=128)


class GradeCreate(BaseModel):
    number: int = Field(ge=-1, le=12)
    title: str = Field(min_length=1, max_length=64)


class GradeUpdate(BaseModel):
    number: int | None = Field(default=None, ge=-1, le=12)
    title: str | None = Field(default=None, min_length=1, max_length=64)


class SkillCreate(BaseModel):
    subject_id: int
    grade_id: int
    code: str = Field(min_length=1, max_length=16)
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    difficulty: int = Field(ge=1, le=5, default=1)
    example_url: str | None = None
    video_url: str | None = None
    is_published: bool = True
    # Код генератора задач - выполняется для создания задач динамически
    generator_code: str | None = Field(default=None, description="Code generator that creates problems dynamically")
    # Метаданные генератора (параметры, настройки)
    generator_metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata for the generator (parameters, settings)")


class SkillUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=16)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] | None = None
    difficulty: int | None = Field(default=None, ge=1, le=5)
    example_url: str | None = None
    video_url: str | None = None
    is_published: bool | None = None


class QuestionCreate(BaseModel):
    skill_id: int
    type: QuestionType
    prompt: str
    data: dict[str, Any] = Field(default_factory=dict)
    correct_answer: dict[str, Any] = Field(default_factory=dict)
    explanation: str = ""
    level: int = Field(ge=1, le=5, default=1)


class InteractiveQuestionCreate(BaseModel):
    """Специальная схема для создания интерактивных заданий с кодом"""
    skill_id: int
    prompt: str
    component_code: str = Field(description="Vue component code (template + script)")
    correct_answer: dict[str, Any] = Field(default_factory=dict, description="Correct answer structure")
    explanation: str = ""
    level: int = Field(ge=1, le=5, default=1)
    # Метаданные для компонента
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the component")


class PluginQuestionCreate(BaseModel):
    """Добавить плагин в тест (навык). Создаёт вопрос типа PLUGIN."""
    skill_id: int
    plugin_id: str = Field(description="ID плагина из manifest")
    plugin_version: str | None = Field(default=None, description="Версия плагина; если не указана — последняя опубликованная")


class AddPluginToTestRequest(BaseModel):
    """Добавить плагин в тест: создаётся навык из плагина + вопрос PLUGIN."""
    grade_id: int = Field(description="ID класса (grade)")
    plugin_id: str = Field(description="ID плагина из manifest")
    plugin_version: str | None = Field(default=None, description="Версия плагина; если не указана — последняя")


class QuestionUpdate(BaseModel):
    prompt: str | None = None
    data: dict[str, Any] | None = None
    correct_answer: dict[str, Any] | None = None
    explanation: str | None = None
    level: int | None = Field(default=None, ge=1, le=5)


class BulkImportRequest(BaseModel):
    skills: list[SkillCreate] = Field(default_factory=list)
    questions: list[QuestionCreate] = Field(default_factory=list)


class BulkImportResponse(BaseModel):
    skills_created: int
    questions_created: int

