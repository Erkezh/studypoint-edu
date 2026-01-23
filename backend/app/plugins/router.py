from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.core.errors import AppError
from app.db.session import get_db_session
from app.plugins.schemas import PluginEvaluateRequest, PluginEvaluateResponse
from app.plugins.service import PluginService
from app.schemas.base import ApiResponse

router = APIRouter()


def get_plugin_service(session: AsyncSession = Depends(get_db_session)) -> PluginService:
    """Dependency для получения сервиса плагинов."""
    return PluginService(session)


@router.post(
    "/upload",
    response_model=ApiResponse[dict],
    dependencies=[Depends(require_roles("ADMIN"))],
    tags=["Plugins"],
)
async def upload_plugin(
    file: UploadFile = File(..., description="ZIP файл с плагином"),
    service: PluginService = Depends(get_plugin_service),
):
    """Загружает плагин из ZIP файла.
    
    Требования:
    - Роль: ADMIN
    - Файл должен быть ZIP архивом
    - В корне архива должен быть manifest.json
    - manifest.json должен соответствовать JSON Schema
    - Entry файл должен существовать в архиве
    """
    if not file.filename or not file.filename.endswith(".zip"):
        raise AppError(status_code=400, code="invalid_file", message="Файл должен быть ZIP архивом")
    
    result = await service.upload_plugin(file)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=ApiResponse[list[dict]],
    dependencies=[Depends(require_roles("ADMIN"))],
    tags=["Plugins"],
)
async def list_plugins(service: PluginService = Depends(get_plugin_service)):
    """Получить список всех загруженных плагинов.
    
    Требования:
    - Роль: ADMIN
    """
    plugins = await service.list_plugins()
    return ApiResponse(data=plugins)


@router.post(
    "/{plugin_id}/publish",
    response_model=ApiResponse[dict],
    dependencies=[Depends(require_roles("ADMIN"))],
    tags=["Plugins"],
)
async def publish_plugin(
    plugin_id: str,
    is_published: bool = True,
    service: PluginService = Depends(get_plugin_service),
):
    """Опубликовать или скрыть плагин.
    
    Требования:
    - Роль: ADMIN
    - Query параметр is_published (true/false)
    """
    result = await service.publish_plugin(plugin_id, is_published)
    return ApiResponse(data=result)


@router.delete(
    "/{plugin_id}",
    response_model=ApiResponse[dict],
    dependencies=[Depends(require_roles("ADMIN"))],
    tags=["Plugins"],
)
async def delete_plugin(
    plugin_id: str,
    service: PluginService = Depends(get_plugin_service),
):
    """Удаляет плагин (только если не опубликован).
    
    Требования:
    - Роль: ADMIN
    - Плагин не должен быть опубликован
    """
    result = await service.delete_plugin(plugin_id)
    return ApiResponse(data=result)


@router.post(
    "/evaluate",
    response_model=ApiResponse[PluginEvaluateResponse],
    tags=["Plugins"],
)
async def evaluate_answer(
    request: PluginEvaluateRequest,
    service: PluginService = Depends(get_plugin_service),
):
    """Проверяет ответ пользователя от плагина.
    
    Этот эндпоинт вызывается из iframe плагина через postMessage.
    Плагин отправляет userAnswer, сервер проверяет и возвращает результат.
    
    Публичный эндпоинт (не требует авторизации для упрощения),
    но в продакшене можно добавить проверку токена.
    """
    result = await service.evaluate_answer(
        plugin_id=request.plugin_id,
        task_id=request.task_id,
        user_answer=request.user_answer,
    )
    return ApiResponse(data=PluginEvaluateResponse(**result))
