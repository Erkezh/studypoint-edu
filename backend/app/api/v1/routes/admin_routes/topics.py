from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.rbac import require_roles
from app.schemas.admin import TopicCreate, TopicUpdate
from app.schemas.base import ApiResponse, PaginatedMeta
from app.schemas.catalog import TopicResponse, SkillListItem
from app.services.admin_service import AdminService
from app.models.topic import Topic
from app.models.catalog import Skill
from app.db.session import get_db_session

router = APIRouter(dependencies=[Depends(require_roles("ADMIN"))])


def _topic_to_response(t: Topic) -> TopicResponse:
    return TopicResponse(
        id=t.id,
        slug=t.slug,
        title=t.title,
        description=t.description,
        icon=t.icon,
        order=t.order,
        is_published=t.is_published,
        parent_id=t.parent_id,
    )


@router.get("", response_model=ApiResponse[list[TopicResponse]])
async def list_topics(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    svc: AdminService = Depends(),
):
    rows, total = await svc.list_topics(page=page, page_size=page_size)
    items = [_topic_to_response(t) for t in rows]
    return ApiResponse(data=items, meta=PaginatedMeta(page=page, page_size=page_size, total=total))


@router.get("/{topic_id}")
async def get_topic_detail(topic_id: int, session=Depends(get_db_session)):
    """Return a topic with its subthemes and each subtheme's skills."""
    topic = await session.get(Topic, topic_id)
    if topic is None:
        from app.core.exceptions import AppError
        raise AppError(status_code=404, code="not_found", message="Topic not found")

    # Subthemes
    sub_stmt = select(Topic).where(Topic.parent_id == topic_id).order_by(Topic.order)
    sub_rows = (await session.execute(sub_stmt)).scalars().all()

    # Skills for this topic and all subthemes
    all_topic_ids = [topic_id] + [s.id for s in sub_rows]
    skill_stmt = (
        select(Skill)
        .where(Skill.topic_id.in_(all_topic_ids))
        .order_by(Skill.code)
    )
    skill_rows = (await session.execute(skill_stmt)).scalars().all()

    skills_by_topic: dict[int, list] = {}
    for sk in skill_rows:
        tid = sk.topic_id or topic_id
        skills_by_topic.setdefault(tid, []).append({
            "id": sk.id,
            "subject_id": sk.subject_id,
            "grade_id": sk.grade_id,
            "topic_id": sk.topic_id,
            "code": sk.code,
            "title": sk.title,
            "difficulty": sk.difficulty,
            "tags": sk.tags or [],
            "is_published": sk.is_published,
        })

    subthemes_data = []
    for s in sub_rows:
        subthemes_data.append({
            "id": s.id,
            "slug": s.slug,
            "title": s.title,
            "description": s.description,
            "icon": s.icon,
            "order": s.order,
            "is_published": s.is_published,
            "parent_id": s.parent_id,
            "skills": skills_by_topic.get(s.id, []),
        })

    return ApiResponse(data={
        "id": topic.id,
        "slug": topic.slug,
        "title": topic.title,
        "description": topic.description,
        "icon": topic.icon,
        "order": topic.order,
        "is_published": topic.is_published,
        "parent_id": topic.parent_id,
        "subthemes": subthemes_data,
        "skills": skills_by_topic.get(topic_id, []),
    })


@router.post("", response_model=ApiResponse[TopicResponse])
async def create_topic(body: TopicCreate, svc: AdminService = Depends()):
    t = await svc.create_topic(body)
    return ApiResponse(data=_topic_to_response(t))


@router.patch("/{topic_id}", response_model=ApiResponse[TopicResponse])
async def update_topic(topic_id: int, body: TopicUpdate, svc: AdminService = Depends()):
    t = await svc.update_topic(topic_id, body)
    return ApiResponse(data=_topic_to_response(t))


@router.delete("/{topic_id}", response_model=ApiResponse[dict])
async def delete_topic(topic_id: int, svc: AdminService = Depends()):
    await svc.delete_topic(topic_id)
    return ApiResponse(data={"ok": True})

