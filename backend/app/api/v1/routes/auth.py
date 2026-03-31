from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.rate_limit import rate_limit_dep
from app.schemas.auth import (
    AuthChildrenResponse,
    AuthLoginRequest,
    AuthRefreshRequest,
    AuthRegisterFamilyRequest,
    AuthRegisterRequest,
    AuthTokensResponse,
    AuthFamilyResponse,
    FamilyMemberResponse,
    LogoutRequest,
    SwitchProfileRequest,
)
from app.schemas.base import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=ApiResponse[AuthTokensResponse],
    responses={400: {"model": ApiResponse}, 409: {"model": ApiResponse}},
)
async def register(
    request: Request,
    body: AuthRegisterRequest,
    svc: AuthService = Depends(),
    _rl: None = Depends(rate_limit_dep(limit=settings.auth_rate_limit, window_sec=settings.auth_rate_window_sec)),
):
    tokens = await svc.register(body)
    return ApiResponse(data=tokens)


@router.post(
    "/register/family",
    response_model=ApiResponse[AuthTokensResponse],
    responses={400: {"model": ApiResponse}, 409: {"model": ApiResponse}},
)
async def register_family(
    request: Request,
    body: AuthRegisterFamilyRequest,
    svc: AuthService = Depends(),
    _rl: None = Depends(rate_limit_dep(limit=settings.auth_rate_limit, window_sec=settings.auth_rate_window_sec)),
):
    tokens = await svc.register_family(body)
    return ApiResponse(data=tokens)


@router.post(
    "/login",
    response_model=ApiResponse[AuthTokensResponse],
)
async def login(
    request: Request,
    body: AuthLoginRequest,
    svc: AuthService = Depends(),
    _rl: None = Depends(rate_limit_dep(limit=settings.auth_rate_limit, window_sec=settings.auth_rate_window_sec)),
):
    tokens = await svc.login(body)
    return ApiResponse(data=tokens)


@router.post("/switch-profile", response_model=ApiResponse[AuthTokensResponse])
async def switch_profile(
    body: SwitchProfileRequest,
    user=Depends(get_current_user),
    svc: AuthService = Depends(),
):
    tokens = await svc.switch_profile(current_user_id=str(user.id), target_user_id=str(body.target_user_id))
    return ApiResponse(data=tokens)


@router.get("/me/family", response_model=ApiResponse[AuthFamilyResponse])
async def get_family_members(
    user=Depends(get_current_user),
    svc: AuthService = Depends(),
):
    members_data = await svc.get_family_members(user)
    members = [
        FamilyMemberResponse(
            id=m["id"],
            full_name=m["full_name"],
            role=m["role"],
            grade_level=m["grade_level"],
            is_current=m["is_current"],
        )
        for m in members_data
    ]
    return ApiResponse(data=AuthFamilyResponse(members=members))


@router.post("/refresh", response_model=ApiResponse[AuthTokensResponse])
async def refresh(
    body: AuthRefreshRequest,
    svc: AuthService = Depends(),
):
    tokens = await svc.refresh(body.refresh_token)
    return ApiResponse(data=tokens)


@router.post("/logout", response_model=ApiResponse[dict])
async def logout(body: LogoutRequest, svc: AuthService = Depends()):
    await svc.logout(body.refresh_token)
    return ApiResponse(data={"ok": True})

