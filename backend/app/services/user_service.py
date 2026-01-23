from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.repositories.user_repo import UserRepository
from app.schemas.user import StudentProfileResponse, SubscriptionResponse, UserMeResponse
import uuid


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.users = UserRepository(session)

    async def get_me(self, *, user_id: str | uuid.UUID) -> UserMeResponse:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise AppError(status_code=404, code="not_found", message="User not found")
        profile = user.profile
        sub = await self.users.get_subscription(user.id)
        return UserMeResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            profile=StudentProfileResponse(grade_level=profile.grade_level, school=profile.school) if profile else None,
            subscription=SubscriptionResponse(plan=sub.plan, is_active=sub.is_active) if sub else None,
        )
