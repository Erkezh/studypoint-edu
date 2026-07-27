from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.rbac import require_roles
from app.schemas.base import ApiResponse
from app.schemas.family import FamilyAddChildRequest, FamilyAddChildResponse
from app.services.family_service import FamilyService

router = APIRouter(dependencies=[Depends(require_roles("PARENT"))])

@router.post("/children", response_model=ApiResponse[FamilyAddChildResponse])
async def add_child(
    body: FamilyAddChildRequest,
    user=Depends(get_current_user),
    svc: FamilyService = Depends(),
):
    return ApiResponse(data=await svc.add_child(parent_id=user.id, req=body))

@router.get("/analytics", response_model=ApiResponse[list[dict]])
async def get_analytics(
    user=Depends(get_current_user),
    svc: FamilyService = Depends(),
):
    return ApiResponse(data=await svc.get_analytics(parent_id=user.id))
