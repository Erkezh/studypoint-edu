from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    """Схема manifest.json плагина.
    
    Все поля обязательны согласно JSON Schema валидации.
    """
    id: str = Field(..., description="Уникальный идентификатор плагина")
    name: str = Field(..., description="Название плагина")
    version: str = Field(..., description="Версия плагина (semver)")
    entry: str = Field(..., description="Entry point файл")
    api_version: str = Field(..., alias="apiVersion", description="Версия API")
    capabilities: dict[str, bool] = Field(default_factory=dict, description="Возможности плагина")
    height: int = Field(default=400, ge=200, le=2000, description="Высота iframe")

    model_config = {"populate_by_name": True}


class PluginCreate(BaseModel):
    """Схема для создания плагина (после валидации manifest)."""
    id: str
    name: str
    version: str
    entry: str
    api_version: str
    capabilities: dict[str, bool]
    height: int
    manifest_data: dict[str, Any]


class PluginResponse(BaseModel):
    """Схема ответа с информацией о плагине."""
    id: str
    name: str
    version: str
    entry: str
    api_version: str
    capabilities: dict[str, bool]
    height: int
    is_published: bool
    created_at: str
    updated_at: str


class PluginEvaluateRequest(BaseModel):
    """Схема запроса на проверку ответа от плагина.
    
    Плагин отправляет userAnswer через postMessage,
    сервер проверяет и возвращает результат.
    """
    task_id: str = Field(..., description="ID задания (может быть question_id или session_id)")
    user_answer: dict[str, Any] = Field(..., alias="userAnswer", description="Ответ пользователя")
    plugin_id: str = Field(..., description="ID плагина для определения логики проверки")

    model_config = {"populate_by_name": True}


class PluginEvaluateResponse(BaseModel):
    """Схема ответа с результатом проверки.
    
    Отправляется обратно в плагин через postMessage.
    """
    correct: bool
    score: float = Field(ge=0.0, le=1.0, description="Оценка от 0.0 до 1.0")
    explanation: str = Field(default="", description="Объяснение ошибки или правильного ответа")
