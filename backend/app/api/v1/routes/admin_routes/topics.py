from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.rbac import require_roles
from app.schemas.admin import TopicCreate, TopicUpdate
from app.schemas.base import ApiResponse, PaginatedMeta
from app.schemas.catalog import TopicResponse
from app.services.admin_service import AdminService

router = APIRouter(dependencies=[Depends(require_roles("ADMIN"))])


@router.get("", response_model=ApiResponse[list[TopicResponse]])
async def list_topics(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    svc: AdminService = Depends(),
):
    rows, total = await svc.list_topics(page=page, page_size=page_size)
    items = [
        TopicResponse(
            id=t.id,
            slug=t.slug,
            title=t.title,
            description=t.description,
            icon=t.icon,
            order=t.order,
            is_published=t.is_published,
        )
        for t in rows
    ]
    return ApiResponse(data=items, meta=PaginatedMeta(page=page, page_size=page_size, total=total))


@router.post("", response_model=ApiResponse[TopicResponse])
async def create_topic(body: TopicCreate, svc: AdminService = Depends()):
    t = await svc.create_topic(body)
    return ApiResponse(
        data=TopicResponse(
            id=t.id,
            slug=t.slug,
            title=t.title,
            description=t.description,
            icon=t.icon,
            order=t.order,
            is_published=t.is_published,
        )
    )


@router.patch("/{topic_id}", response_model=ApiResponse[TopicResponse])
async def update_topic(topic_id: int, body: TopicUpdate, svc: AdminService = Depends()):
    t = await svc.update_topic(topic_id, body)
    return ApiResponse(
        data=TopicResponse(
            id=t.id,
            slug=t.slug,
            title=t.title,
            description=t.description,
            icon=t.icon,
            order=t.order,
            is_published=t.is_published,
        )
    )


@router.delete("/{topic_id}", response_model=ApiResponse[dict])
async def delete_topic(topic_id: int, svc: AdminService = Depends()):
    await svc.delete_topic(topic_id)
    return ApiResponse(data={"ok": True})
