from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Path

from app.core.rbac import require_roles
from app.schemas.admin import AdminSubscriptionResponse, AdminSubscriptionUpdate
from app.schemas.base import ApiResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("", response_model=ApiResponse[list[AdminSubscriptionResponse]], dependencies=[Depends(require_roles("ADMIN"))])
async def list_subscriptions(svc: AdminService = Depends()):
    subs = await svc.list_subscriptions()
    return ApiResponse(data=[
        AdminSubscriptionResponse(
            user_id=str(s.user_id),
            user_email=s.user.email if s.user else "",
            user_name=s.user.full_name if s.user else "",
            plan=s.plan.value if s.plan else "FREE",
            is_active=s.is_active,
            active_until=s.active_until.isoformat() if s.active_until else None,
        )
        for s in subs
    ])


@router.patch("/{user_id}", response_model=ApiResponse[AdminSubscriptionResponse], dependencies=[Depends(require_roles("ADMIN"))])
async def update_subscription(
    body: AdminSubscriptionUpdate,
    user_id: str = Path(...),
    svc: AdminService = Depends()
):
    s = await svc.update_subscription(user_id, body.model_dump(exclude_unset=True))
    return ApiResponse(data=AdminSubscriptionResponse(
        user_id=str(s.user_id),
        user_email=s.user.email if s.user else "",
        user_name=s.user.full_name if s.user else "",
        plan=s.plan.value if s.plan else "FREE",
        is_active=s.is_active,
        active_until=s.active_until.isoformat() if s.active_until else None,
    ))


@router.post("/{user_id}", response_model=ApiResponse[AdminSubscriptionResponse], dependencies=[Depends(require_roles("ADMIN"))])
async def create_subscription(
    body: AdminSubscriptionUpdate,
    user_id: str = Path(...),
    svc: AdminService = Depends()
):
    s = await svc.create_subscription(user_id, body.model_dump(exclude_unset=True))
    return ApiResponse(data=AdminSubscriptionResponse(
        user_id=str(s.user_id),
        user_email=s.user.email if s.user else "",
        user_name=s.user.full_name if s.user else "",
        plan=s.plan.value if s.plan else "FREE",
        is_active=s.is_active,
        active_until=s.active_until.isoformat() if s.active_until else None,
    ))
