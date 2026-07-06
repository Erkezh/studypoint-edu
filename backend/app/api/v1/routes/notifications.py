from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.base import ApiResponse
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=ApiResponse[list[NotificationResponse]])
async def get_my_notifications(
    user=Depends(get_current_user),
    svc: NotificationService = Depends(),
):
    return ApiResponse(data=await svc.get_my_notifications(user_id=user.id))


@router.post("/{notification_id}/read", response_model=ApiResponse[bool])
async def mark_as_read(
    notification_id: str,
    user=Depends(get_current_user),
    svc: NotificationService = Depends(),
):
    success = await svc.mark_as_read(notification_id=notification_id, user_id=user.id)
    return ApiResponse(data=success)


@router.post("/read-all", response_model=ApiResponse[bool])
async def mark_all_as_read(
    user=Depends(get_current_user),
    svc: NotificationService = Depends(),
):
    await svc.mark_all_as_read(user_id=user.id)
    return ApiResponse(data=True)
