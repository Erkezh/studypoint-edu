from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user, get_current_user_optional, get_or_create_guest_user
from app.schemas.base import ApiResponse, PaginatedMeta
from app.schemas.catalog import (
    GradeResponse,
    SkillDetailResponse,
    SkillListItem,
    SubjectResponse,
)
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/subjects", response_model=ApiResponse[list[SubjectResponse]])
async def list_subjects(svc: CatalogService = Depends()):
    return ApiResponse(data=await svc.list_subjects())


@router.get("/grades", response_model=ApiResponse[list[GradeResponse]])
async def list_grades(svc: CatalogService = Depends()):
    return ApiResponse(data=await svc.list_grades())


@router.get("/skills", response_model=ApiResponse[list[SkillListItem]])
async def list_skills(
    subject_slug: str | None = Query(default=None),
    grade_number: int | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    svc: CatalogService = Depends(),
):
    items, total = await svc.list_skills(
        subject_slug=subject_slug,
        grade_number=grade_number,
        query=q,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=items, meta=PaginatedMeta(page=page, page_size=page_size, total=total))


@router.get("/skills/{skill_id}", response_model=ApiResponse[SkillDetailResponse])
async def get_skill(skill_id: int, svc: CatalogService = Depends()):
    return ApiResponse(data=await svc.get_skill(skill_id))


@router.get("/skills/{skill_id}/stats", response_model=ApiResponse[dict])
async def skill_stats(
    skill_id: int,
    svc: CatalogService = Depends(),
    user=Depends(get_current_user_optional),
    guest_user=Depends(get_or_create_guest_user),
):
    # Используем авторизованного пользователя или guest пользователя
    effective_user = user if user is not None else guest_user
    return ApiResponse(data=await svc.get_skill_stats(user_id=effective_user.id, skill_id=skill_id))
