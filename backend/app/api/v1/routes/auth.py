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
    ChildProfileResponse,
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
    tokens = await svc.switch_profile(parent_id=str(user.id), child_id=str(body.child_id))
    return ApiResponse(data=tokens)


@router.get("/me/children", response_model=ApiResponse[AuthChildrenResponse])
async def get_children(
    user=Depends(get_current_user),
    svc: AuthService = Depends(),
):
    children = await svc.users.get_children_by_parent_id(user.id)
    child_profiles = []
    for c in children:
        child_profiles.append(ChildProfileResponse(
            id=c.id,
            full_name=c.full_name,
            grade_level=c.profile.grade_level if c.profile else 0,
            school=c.profile.school if c.profile else None,
        ))
    return ApiResponse(data=AuthChildrenResponse(children=child_profiles))


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

