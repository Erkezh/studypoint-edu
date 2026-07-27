from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.rbac import require_roles
from app.schemas.admin import BulkImportRequest, InteractiveQuestionCreate, PluginQuestionCreate, QuestionCreate, QuestionUpdate
from app.schemas.base import ApiResponse, PaginatedMeta
from app.services.admin_service import AdminService

router = APIRouter(dependencies=[Depends(require_roles("ADMIN"))])


@router.get("", response_model=ApiResponse[list[dict]])
async def list_questions(
    skill_id: int | None = Query(default=None),
    search: str | None = Query(default=None, description="Поиск по названию навыка"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Сортировка: asc (старые первые) или desc (новые первые)"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    svc: AdminService = Depends(),
):
    rows, total, skill_names = await svc.list_questions(page=page, page_size=page_size, skill_id=skill_id, search=search, sort_order=sort_order)
    items = [
        {
            "id": q.id,
            "skill_id": q.skill_id,
            "skill_title": skill_names.get(q.skill_id, ""),
            "type": q.type,
            "prompt": q.prompt,
            "data": q.data,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "level": q.level,
            "created_at": q.created_at.isoformat() if q.created_at else None,
        }
        for q in rows
    ]
    return ApiResponse(data=items, meta=PaginatedMeta(page=page, page_size=page_size, total=total))


@router.post("", response_model=ApiResponse[dict])
async def create_question(body: QuestionCreate, svc: AdminService = Depends()):
    q = await svc.create_question(body)
    return ApiResponse(
        data={
            "id": q.id,
            "skill_id": q.skill_id,
            "type": q.type,
            "prompt": q.prompt,
            "data": q.data,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "level": q.level,
        }
    )


@router.patch("/{question_id}", response_model=ApiResponse[dict])
async def update_question(question_id: int, body: QuestionUpdate, svc: AdminService = Depends()):
    q = await svc.update_question(question_id, body)
    return ApiResponse(
        data={
            "id": q.id,
            "skill_id": q.skill_id,
            "type": q.type,
            "prompt": q.prompt,
            "data": q.data,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "level": q.level,
        }
    )


@router.delete("/{question_id}", response_model=ApiResponse[dict])
async def delete_question(question_id: int, svc: AdminService = Depends()):
    await svc.delete_question(question_id)
    return ApiResponse(data={"ok": True})


@router.post("/bulk_import", response_model=ApiResponse[dict])
async def bulk_import(body: BulkImportRequest, svc: AdminService = Depends()):
    res = await svc.bulk_import(body)
    return ApiResponse(data=res.model_dump(mode="json"))


@router.post("/interactive", response_model=ApiResponse[dict])
async def create_interactive_question(body: InteractiveQuestionCreate, svc: AdminService = Depends()):
    """Создание интерактивного задания с кодом компонента"""
    from app.models.enums import QuestionType
    
    # Создаем вопрос с типом INTERACTIVE
    # component_code сохраняется в data, а не как отдельное поле
    question_data = QuestionCreate(
        skill_id=body.skill_id,
        type=QuestionType.INTERACTIVE,
        prompt=body.prompt,
        data={
            "component_code": body.component_code,
            "metadata": body.metadata or {},
        },
        correct_answer=body.correct_answer or {},
        explanation=body.explanation or "",
        level=body.level or 1,
    )
    q = await svc.create_question(question_data)
    return ApiResponse(
        data={
            "id": q.id,
            "skill_id": q.skill_id,
            "type": q.type,
            "prompt": q.prompt,
            "data": q.data,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "level": q.level,
        }
    )


@router.post("/plugin", response_model=ApiResponse[dict])
async def create_plugin_question(body: PluginQuestionCreate, svc: AdminService = Depends()):
    """Добавить плагин в тест (навык). Создаёт вопрос типа PLUGIN."""
    q = await svc.create_plugin_question(body)
    return ApiResponse(
        data={
            "id": q.id,
            "skill_id": q.skill_id,
            "type": q.type,
            "prompt": q.prompt,
            "data": q.data,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "level": q.level,
        }
    )

