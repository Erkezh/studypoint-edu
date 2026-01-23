from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.base import ApiResponse
from app.schemas.user import UserMeResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=ApiResponse[UserMeResponse])
async def me(
    user=Depends(get_current_user),
    svc: UserService = Depends(),
):
    me = await svc.get_me(user_id=user.id)
    return ApiResponse(data=me)

