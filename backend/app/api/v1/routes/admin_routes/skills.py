from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.rbac import require_roles
from app.schemas.admin import SkillCreate, SkillUpdate
from app.schemas.base import ApiResponse, PaginatedMeta
from app.schemas.catalog import SkillDetailResponse, SkillListItem
from app.services.admin_service import AdminService

router = APIRouter(dependencies=[Depends(require_roles("ADMIN"))])


@router.get("", response_model=ApiResponse[list[SkillListItem]])
async def list_skills(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    svc: AdminService = Depends(),
):
    rows, total = await svc.list_skills(page=page, page_size=page_size)
    items = [
        SkillListItem(
            id=s.id,
            subject_id=s.subject_id,
            grade_id=s.grade_id,
            code=s.code,
            title=s.title,
            difficulty=s.difficulty,
            tags=s.tags,
        )
        for s in rows
    ]
    return ApiResponse(data=items, meta=PaginatedMeta(page=page, page_size=page_size, total=total))


@router.post("", response_model=ApiResponse[SkillDetailResponse])
async def create_skill(body: SkillCreate, svc: AdminService = Depends()):
    s = await svc.create_skill(body)
    return ApiResponse(
        data=SkillDetailResponse(
            id=s.id,
            subject_id=s.subject_id,
            grade_id=s.grade_id,
            code=s.code,
            title=s.title,
            difficulty=s.difficulty,
            tags=s.tags,
            description=s.description,
            example_url=s.example_url,
            video_url=s.video_url,
            is_published=s.is_published,
        )
    )


@router.patch("/{skill_id}", response_model=ApiResponse[SkillDetailResponse])
async def update_skill(skill_id: int, body: SkillUpdate, svc: AdminService = Depends()):
    s = await svc.update_skill(skill_id, body)
    return ApiResponse(
        data=SkillDetailResponse(
            id=s.id,
            subject_id=s.subject_id,
            grade_id=s.grade_id,
            code=s.code,
            title=s.title,
            difficulty=s.difficulty,
            tags=s.tags,
            description=s.description,
            example_url=s.example_url,
            video_url=s.video_url,
            is_published=s.is_published,
        )
    )


@router.delete("/{skill_id}", response_model=ApiResponse[dict])
async def delete_skill(skill_id: int, svc: AdminService = Depends()):
    await svc.delete_skill(skill_id)
    return ApiResponse(data={"ok": True})

