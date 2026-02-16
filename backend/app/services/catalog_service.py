from __future__ import annotations

import json
import logging

from fastapi import Depends
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.db.session import get_db_session
from app.repositories.catalog_repo import GradeRepository, SkillRepository, SubjectRepository, TopicRepository
from app.repositories.practice_repo import PracticeRepository
from app.schemas.catalog import GradeResponse, SkillDetailResponse, SkillListItem, SkillUpdate, SubjectResponse, TopicResponse
from app.utils.redis import get_redis

logger = logging.getLogger(__name__)


class CatalogService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.subjects = SubjectRepository(session)
        self.grades = GradeRepository(session)
        self.topics = TopicRepository(session)
        self.skills = SkillRepository(session)
        self.practice = PracticeRepository(session)

    async def _cache_get(self, key: str) -> str | None:
        try:
            redis = get_redis()
            return await redis.get(key)
        except RedisError as exc:
            logger.warning("Cache read failed for key %s: %s", key, exc)
            return None

    async def _cache_setex(self, key: str, value: str) -> None:
        try:
            redis = get_redis()
            await redis.setex(key, settings.cache_ttl_sec, value)
        except RedisError as exc:
            logger.warning("Cache write failed for key %s: %s", key, exc)

    async def _cache_delete(self, key: str) -> None:
        try:
            redis = get_redis()
            await redis.delete(key)
        except RedisError as exc:
            logger.warning("Cache delete failed for key %s: %s", key, exc)

    async def list_subjects(self) -> list[SubjectResponse]:
        key = "cache:subjects"
        cached = await self._cache_get(key)
        if cached:
            return [SubjectResponse.model_validate(x) for x in json.loads(cached)]
        rows = await self.subjects.list()
        data = [SubjectResponse(id=s.id, slug=s.slug, title=s.title) for s in rows]
        await self._cache_setex(key, json.dumps([d.model_dump(mode="json") for d in data]))
        return data

    async def list_grades(self) -> list[GradeResponse]:
        key = "cache:grades"
        cached = await self._cache_get(key)
        if cached:
            return [GradeResponse.model_validate(x) for x in json.loads(cached)]
        rows = await self.grades.list()
        data = [GradeResponse(id=g.id, number=g.number, title=g.title) for g in rows]
        await self._cache_setex(key, json.dumps([d.model_dump(mode="json") for d in data]))
        return data

    async def list_topics(self) -> list[TopicResponse]:
        key = "cache:topics"
        cached = await self._cache_get(key)
        if cached:
            return [TopicResponse.model_validate(x) for x in json.loads(cached)]
        rows = await self.topics.list(published_only=True)
        data = [TopicResponse(
            id=t.id,
            slug=t.slug,
            title=t.title,
            description=t.description,
            icon=t.icon,
            order=t.order,
            is_published=t.is_published,
        ) for t in rows]
        await self._cache_setex(key, json.dumps([d.model_dump(mode="json") for d in data]))
        return data

    async def list_skills(
        self,
        *,
        subject_slug: str | None,
        grade_number: int | None,
        topic_id: int | None = None,
        query: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[SkillListItem], int]:
        key = f"cache:skills:{subject_slug}:{grade_number}:{topic_id}:{query}:{page}:{page_size}"
        cached = await self._cache_get(key)
        if cached:
            payload = json.loads(cached)
            return ([SkillListItem.model_validate(x) for x in payload["items"]], payload["total"])

        subject_id = None
        if subject_slug:
            subject = await self.subjects.get_by_slug(subject_slug)
            if subject is None:
                return ([], 0)
            subject_id = subject.id
        grade_id = None
        if grade_number is not None:
            grade = await self.grades.get_by_number(grade_number)
            if grade is None:
                return ([], 0)
            grade_id = grade.id

        rows, total = await self.skills.list(
            subject_id=subject_id,
            grade_id=grade_id,
            topic_id=topic_id,
            query=query,
            page=page,
            page_size=page_size,
        )
        items = [
            SkillListItem(
                id=s.id,
                subject_id=s.subject_id,
                grade_id=s.grade_id,
                topic_id=s.topic_id,
                topic_title=s.topic.title if s.topic else None,
                code=s.code,
                title=s.title,
                difficulty=s.difficulty,
                tags=s.tags,
            )
            for s in rows
        ]
        await self._cache_setex(key, json.dumps({"items": [i.model_dump(mode="json") for i in items], "total": total}))
        return items, total

    async def get_skill(self, skill_id: int) -> SkillDetailResponse:
        key = f"cache:skill:{skill_id}"
        cached = await self._cache_get(key)
        if cached:
            return SkillDetailResponse.model_validate_json(cached)

        s = await self.skills.get(skill_id)
        if s is None or not s.is_published:
            raise AppError(status_code=404, code="not_found", message="Skill not found")
        resp = SkillDetailResponse(
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
        await self._cache_setex(key, resp.model_dump_json())
        return resp

    async def update_skill(self, skill_id: int, data: SkillUpdate) -> SkillDetailResponse:
        s = await self.skills.get(skill_id)
        if s is None:
            raise AppError(status_code=404, code="not_found", message="Skill not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
             resp = SkillDetailResponse(
                id=s.id,
                subject_id=s.subject_id,
                grade_id=s.grade_id,
                topic_id=s.topic_id,
                topic_title=s.topic.title if s.topic else None,
                code=s.code,
                title=s.title,
                difficulty=s.difficulty,
                tags=s.tags,
                description=s.description,
                example_url=s.example_url,
                video_url=s.video_url,
                is_published=s.is_published,
            )
             return resp

        updated_skill = await self.skills.update(s, **update_data)

        # Invalidate cache
        # 1. Skill detail cache
        await self._cache_delete(f"cache:skill:{skill_id}")
        # 2. List cache is harder to clear precisely because of pagination keys.
        # For now, we can iterate scan or accept eventual consistency (TTL).
        # Or clear by grade/subject pattern if possible.
        # A simple approach: rely on TTL for lists, but detail is critical.
        # Let's try to clear specific pattern if we knew the old values, but we might have changed them.
        # Ideally we should clear `cache:skills:*` pattern.
        # For this edit feature, immediate feedback is needed.
        # Let's clear ALL skills list cache to be safe and simple for now.
        # Keys are `cache:skills:{subject_slug}:{grade_number}:{topic_id}:{query}:{page}:{page_size}`
        # We can use keys commands but that's slow.
        # Alternatively we can just let lists be stale for 5 mins (CACHE_TTL).
        # But UI might be confusing if item doesn't move.
        # Frontend store manual update will handle UI consistency.

        resp = SkillDetailResponse(
            id=updated_skill.id,
            subject_id=updated_skill.subject_id,
            grade_id=updated_skill.grade_id,
            topic_id=updated_skill.topic_id,
            topic_title=updated_skill.topic.title if updated_skill.topic else None,
            code=updated_skill.code,
            title=updated_skill.title,
            difficulty=updated_skill.difficulty,
            tags=updated_skill.tags,
            description=updated_skill.description,
            example_url=updated_skill.example_url,
            video_url=updated_skill.video_url,
            is_published=updated_skill.is_published,
        )
        return resp

    async def get_skill_stats(self, *, user_id: str, skill_id: int) -> dict:
        # Snapshot is the cheap source of truth for per-skill stats.
        import uuid

        try:
            uid = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        except ValueError as e:
            raise AppError(status_code=400, code="validation_error", message="Invalid user id") from e

        snap = await self.practice.get_snapshot(user_id=uid, skill_id=skill_id)
        if snap is None:
            return {"best_smartscore": 0, "last_smartscore": 0, "last_practiced_at": None, "total_questions": 0, "accuracy_percent": 0}
        return {
            "best_smartscore": snap.best_smartscore,
            "last_smartscore": snap.last_smartscore,
            "last_practiced_at": snap.last_practiced_at,
            "total_questions": snap.total_questions,
            "accuracy_percent": snap.accuracy_percent,
        }
