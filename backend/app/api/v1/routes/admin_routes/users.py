from __future__ import annotations

from fastapi import APIRouter, Depends, Path

from app.core.rbac import require_roles
from app.schemas.admin import AdminUserResponse, AdminUserUpdate
from app.schemas.base import ApiResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/", response_model=ApiResponse[list[AdminUserResponse]], dependencies=[Depends(require_roles("ADMIN"))])
async def list_users(svc: AdminService = Depends()):
    users = await svc.get_users()
    return ApiResponse(data=[
        AdminUserResponse(
            id=str(u.id),
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
        )
        for u in users
    ])


@router.patch("/{user_id}", response_model=ApiResponse[AdminUserResponse], dependencies=[Depends(require_roles("ADMIN"))])
async def update_user(
    body: AdminUserUpdate,
    user_id: str = Path(...),
    svc: AdminService = Depends()
):
    updated = await svc.update_user(user_id, body.model_dump(exclude_unset=True))
    return ApiResponse(data=AdminUserResponse(
        id=str(updated.id),
        email=updated.email,
        full_name=updated.full_name,
        role=updated.role,
        is_active=updated.is_active,
    ))
