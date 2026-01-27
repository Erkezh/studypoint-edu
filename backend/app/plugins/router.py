from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.core.errors import AppError
from app.db.session import get_db_session
from app.plugins.schemas import PluginEvaluateRequest, PluginEvaluateResponse
from app.plugins.service import PluginService
from app.schemas.admin import AddPluginToTestRequest
from app.schemas.base import ApiResponse
from app.services.admin_service import AdminService

router = APIRouter()


def get_plugin_service(session: AsyncSession = Depends(get_db_session)) -> PluginService:
    """Dependency для получения сервиса плагинов."""
    return PluginService(session)


@router.post(
    "/add-to-test",
    response_model=ApiResponse[dict],
    dependencies=[Depends(require_roles("ADMIN"))],
    tags=["Plugins"],
)
async def add_plugin_to_test(body: AddPluginToTestRequest, svc: AdminService = Depends()):
    """Добавить плагин в тест: создаётся навык из плагина + вопрос PLUGIN. Плагин сам является навыком."""
    result = await svc.add_plugin_to_test(body)
    return ApiResponse(data=result)


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


@router.post(
    "/upload-tsx",
    response_model=ApiResponse[dict],
    dependencies=[Depends(require_roles("ADMIN"))],
    tags=["Plugins"],
)
async def upload_tsx_plugin(
    file: UploadFile = File(..., description="TSX файл с React компонентом"),
    plugin_name: str | None = Form(None, description="Название плагина (опционально)"),
    grade_id: int | None = Form(None, description="ID класса для автоматического добавления в тест (опционально)"),
    service: PluginService = Depends(get_plugin_service),
    admin_service: AdminService = Depends(),
):
    """Загружает TSX файл и создает плагин из него.
    
    Требования:
    - Роль: ADMIN
    - Файл должен быть .tsx или .ts
    - Файл должен содержать валидный React компонент
    
    Опционально:
    - plugin_name: Название плагина (если не указано, берется из имени файла)
    - grade_id: ID класса для автоматического добавления в тест
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Upload TSX request: filename={file.filename}, plugin_name={plugin_name}, grade_id={grade_id}")
    
    if not file.filename or not (file.filename.endswith(".tsx") or file.filename.endswith(".ts")):
        raise AppError(
            status_code=400,
            code="invalid_file",
            message="Файл должен быть .tsx или .ts"
        )
    
    try:
        result = await service.upload_tsx_plugin(
            file=file,
            plugin_name=plugin_name,
            grade_id=grade_id,
            admin_service=admin_service,
        )
        logger.info(f"TSX plugin created successfully: {result.get('plugin_id')}")
        return ApiResponse(data=result)
    except Exception as e:
        logger.error(f"Error uploading TSX plugin: {str(e)}", exc_info=True)
        raise
