from __future__ import annotations

from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import QuestionType, UserRole


class SubjectCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=128)


class SubjectUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=128)


class GradeCreate(BaseModel):
    number: int
    label: str = Field(min_length=1, max_length=8)
    title: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1)


class GradeUpdate(BaseModel):
    number: int | None = None
    label: str | None = Field(default=None, max_length=8)
    title: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = None


class TopicCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=128)
    description: str = ""
    icon: str | None = Field(default=None, max_length=64)
    order: int = Field(default=0, ge=0)
    is_published: bool = True
    parent_id: int | None = None


class TopicUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    icon: str | None = None
    order: int | None = Field(default=None, ge=0)
    is_published: bool | None = None
    parent_id: int | None = None


class SkillCreate(BaseModel):
    subject_id: int
    grade_id: int
    topic_id: int | None = None
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
    grade_id: int | None = None
    topic_id: int | None = None
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
    topic_id: int | None = Field(default=None, description="ID темы (topic); если не указан — без темы")
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


class AdminUserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool


class AdminUserUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None


class AdminSubscriptionResponse(BaseModel):
    user_id: str
    user_email: str
    user_name: str
    plan: str
    is_active: bool
    active_until: str | None = None


class AdminSubscriptionUpdate(BaseModel):
    plan: str | None = None
    is_active: bool | None = None
    active_until: str | None = None

