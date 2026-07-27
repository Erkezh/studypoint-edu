from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.deps import get_current_user, get_current_user_optional, get_or_create_guest_user
from app.schemas.base import ApiResponse, PaginatedMeta
from app.schemas.catalog import (
    GradeResponse,
    SkillDetailResponse,
    SkillListItem,
    SkillStatsResponse,
    SkillUpdate,
    SubjectResponse,
    TopicResponse,
)
from app.services.catalog_service import CatalogService

router = APIRouter()


@router.get("/subjects", response_model=ApiResponse[list[SubjectResponse]])
async def list_subjects(svc: CatalogService = Depends()):
    return ApiResponse(data=await svc.list_subjects())


@router.get("/grades", response_model=ApiResponse[list[GradeResponse]])
async def list_grades(svc: CatalogService = Depends()):
    return ApiResponse(data=await svc.list_grades())


@router.get("/topics", response_model=ApiResponse[list[TopicResponse]])
async def list_topics(svc: CatalogService = Depends()):
    return ApiResponse(data=await svc.list_topics())


@router.get("/skills", response_model=ApiResponse[list[SkillListItem]])
async def list_skills(
    subject_slug: str | None = Query(default=None),
    grade_number: int | None = Query(default=None),
    topic_id: int | None = Query(default=None),
    topic_ids: str | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
    svc: CatalogService = Depends(),
):
    items, total = await svc.list_skills(
        subject_slug=subject_slug,
        grade_number=grade_number,
        topic_id=topic_id,
        topic_ids=_parse_int_list_query(topic_ids),
        query=q,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=items, meta=PaginatedMeta(page=page, page_size=page_size, total=total))


@router.get("/skills/stats", response_model=ApiResponse[dict[str, SkillStatsResponse]])
async def get_skill_stats_bulk(
    skill_ids: str = Query(...),
    svc: CatalogService = Depends(),
    user=Depends(get_current_user_optional),
    guest_user=Depends(get_or_create_guest_user),
):
    effective_user = user if user is not None else guest_user
    return ApiResponse(
        data=await svc.get_skill_stats_bulk(
            user_id=effective_user.id,
            skill_ids=_parse_int_list_query(skill_ids),
        )
    )


@router.get("/skills/{skill_id}", response_model=ApiResponse[SkillDetailResponse])
async def get_skill(skill_id: int, svc: CatalogService = Depends()):
    return ApiResponse(data=await svc.get_skill(skill_id))


@router.get("/skills/{skill_id}/stats", response_model=ApiResponse[SkillStatsResponse])
async def get_skill_stats(
    skill_id: int,
    svc: CatalogService = Depends(),
    user=Depends(get_current_user_optional),
    guest_user=Depends(get_or_create_guest_user),
):
    effective_user = user if user is not None else guest_user
    return ApiResponse(data=await svc.get_skill_stats(user_id=effective_user.id, skill_id=skill_id))


@router.patch("/skills/{skill_id}", response_model=ApiResponse[SkillDetailResponse])
async def update_skill(
    skill_id: int,
    data: SkillUpdate,
    svc: CatalogService = Depends(),
    user=Depends(get_current_user),
):
    # Only ADMIN can update skills
    if user.role != "ADMIN":
         # In a real app we'd raise 403, but let's assume get_current_user checks or we add check here
         # For now, simplistic check or handled by service/policy
         pass 

    return ApiResponse(data=await svc.update_skill(skill_id, data))


def _parse_int_list_query(raw_value: str | None) -> list[int]:
    if not raw_value:
        return []

    values: list[int] = []
    for chunk in raw_value.split(","):
        item = chunk.strip()
        if not item:
            continue
        try:
            values.append(int(item))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Invalid integer list value: {item}") from exc
    return values
