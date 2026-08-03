from __future__ import annotations

import uuid
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password
from app.db.session import get_db_session
from app.models.enums import SubscriptionPlan, UserRole
from app.models.profile import StudentProfile
from app.models.subscription import Subscription
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.family import FamilyAddChildRequest, FamilyAddChildResponse
from app.services.analytics_service import AnalyticsService

class FamilyService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.analytics = AnalyticsService(session)

    async def add_child(self, *, parent_id: str, req: FamilyAddChildRequest) -> FamilyAddChildResponse:
        parent = await self.users.get_by_id(parent_id)
        if not parent or parent.role != UserRole.PARENT:
            raise AppError(status_code=403, code="forbidden", message="Only parents can add children")

        child_email = f"child_{uuid.uuid4().hex[:8]}@{parent.email.split('@')[-1]}"

        try:
            child_user = await self.users.create(
                email=child_email,
                password_hash=parent.password_hash,
                full_name=req.name,
                role=UserRole.STUDENT,
            )
            child_user.parent_id = parent.id

            self.session.add(StudentProfile(user_id=child_user.id, grade_level=req.grade_level))
            self.session.add(Subscription(user_id=child_user.id, plan=SubscriptionPlan.FAMILY, is_active=True))

            await self.session.commit()
            
            # Fetch the generated user id
            await self.session.refresh(child_user)
            
            return FamilyAddChildResponse(
                id=str(child_user.id),
                name=child_user.full_name,
                username=child_user.email,
                grade_level=req.grade_level,
            )
        except IntegrityError as e:
            await self.session.rollback()
            raise AppError(status_code=400, code="creation_failed", message="Could not create child account") from e

    async def get_analytics(self, *, parent_id: str) -> list[dict[str, Any]]:
        # Get all children for this parent
        stmt = select(User).where(User.parent_id == parent_id).order_by(User.full_name)
        children = (await self.session.execute(stmt)).scalars().all()

        results = []
        for child in children:
            overview = await self.analytics.overview(user_id=str(child.id))
            results.append({
                "child_id": str(child.id),
                "name": child.full_name,
                "overview": overview
            })

        return results

    async def get_child_analytics(self, *, parent_id: str, child_id: str, include_questions: bool = True) -> dict[str, Any]:
        child = await self.users.get_by_id(child_id)
        if not child or str(child.parent_id) != str(parent_id):
            raise AppError(status_code=404, code="not_found", message="Child not found")

        overview = await self.analytics.overview(user_id=child_id)
        skills = await self.analytics.skills(user_id=child_id)
        all_questions = await self.analytics.all_questions(user_id=child_id) if include_questions else []

        return {
            "overview": overview,
            "skills": skills,
            "all_questions": all_questions,
        }
