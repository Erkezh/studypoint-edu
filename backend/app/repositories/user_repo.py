from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.subscription import Subscription
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: str | uuid.UUID) -> User | None:
        try:
            uid = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        except ValueError:
            return None
        stmt = select(User).where(User.id == uid).options(selectinload(User.profile), selectinload(User.subscription))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).options(selectinload(User.profile), selectinload(User.subscription))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def create(self, *, email: str, password_hash: str, full_name: str, role) -> User:
        user = User(email=email, password_hash=password_hash, full_name=full_name, role=role, is_active=True)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_subscription(self, user_id: uuid.UUID) -> Subscription | None:
        return (await self.session.execute(select(Subscription).where(Subscription.user_id == user_id))).scalar_one_or_none()
