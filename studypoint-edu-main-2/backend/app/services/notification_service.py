from __future__ import annotations

import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.notification import Notification
from app.repositories.notification_repo import NotificationRepository
from app.schemas.notification import NotificationResponse


class NotificationService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.notifications = NotificationRepository(session)

    async def get_my_notifications(self, *, user_id: str) -> list[NotificationResponse]:
        uid = _parse_uuid(user_id)
        # Check if we should automatically generate welcome notification if there are no notifications at all
        rows = await self.notifications.list_for_user(uid)
        if len(rows) == 0:
            # Seed a few helpful demo notifications so the feature works out of the box with data!
            welcome_notif = Notification(
                user_id=uid,
                title="StudyPoint-ке қош келдіңіз!",
                content="Оқу платформамызға қосылғаныңыз үшін рахмет. Оқуды бастау үшін 'Оқу' бөліміне өтіңіз!",
                is_read=False
            )
            award_notif = Notification(
                user_id=uid,
                title="Оқуды бастауға дайынсыз ба?",
                content="Диагностикадан өтіп, өз біліміңізді тексеріңіз және алғашқы марапатыңызды алыңыз!",
                is_read=False
            )
            await self.notifications.create(welcome_notif)
            await self.notifications.create(award_notif)
            await self.session.flush()
            rows = await self.notifications.list_for_user(uid)

        return [
            NotificationResponse(
                id=r.id,
                user_id=r.user_id,
                title=r.title,
                content=r.content,
                is_read=r.is_read,
                created_at=r.created_at,
            )
            for r in rows
        ]

    async def create_notification(self, *, user_id: str, title: str, content: str) -> NotificationResponse:
        uid = _parse_uuid(user_id)
        notif = Notification(
            user_id=uid,
            title=title,
            content=content,
            is_read=False
        )
        await self.notifications.create(notif)
        await self.session.flush()
        return NotificationResponse(
            id=notif.id,
            user_id=notif.user_id,
            title=notif.title,
            content=notif.content,
            is_read=notif.is_read,
            created_at=notif.created_at
        )

    async def mark_as_read(self, *, notification_id: str, user_id: str) -> bool:
        nid = _parse_uuid(notification_id)
        uid = _parse_uuid(user_id)
        res = await self.notifications.mark_as_read(nid, uid)
        await self.session.flush()
        return res

    async def mark_all_as_read(self, *, user_id: str) -> None:
        uid = _parse_uuid(user_id)
        await self.notifications.mark_all_as_read(uid)
        await self.session.flush()


def _parse_uuid(value: str | None) -> uuid.UUID:
    if value is None:
        raise AppError(status_code=400, code="validation_error", message="Invalid id")
    try:
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))
    except ValueError as e:
        raise AppError(status_code=400, code="validation_error", message="Invalid id") from e
