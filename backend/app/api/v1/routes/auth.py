from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.errors import AppError
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


def set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.jwt_refresh_ttl_sec,
        httponly=True,
        secure=settings.environment != "local",
        samesite="lax",
    )


def delete_refresh_cookie(response: Response):
    response.delete_cookie(
        key="refresh_token",
        secure=settings.environment != "local",
        samesite="lax",
    )


@router.post(
    "/register",
    response_model=ApiResponse[AuthTokensResponse],
    responses={400: {"model": ApiResponse}, 409: {"model": ApiResponse}},
)
async def register(
    request: Request,
    response: Response,
    body: AuthRegisterRequest,
    svc: AuthService = Depends(),
    _rl: None = Depends(rate_limit_dep(limit=settings.auth_rate_limit, window_sec=settings.auth_rate_window_sec)),
):
    tokens = await svc.register(body)
    set_refresh_cookie(response, tokens.refresh_token)
    return ApiResponse(data=tokens)


@router.post(
    "/register/family",
    response_model=ApiResponse[AuthTokensResponse],
    responses={400: {"model": ApiResponse}, 409: {"model": ApiResponse}},
)
async def register_family(
    request: Request,
    response: Response,
    body: AuthRegisterFamilyRequest,
    svc: AuthService = Depends(),
    _rl: None = Depends(rate_limit_dep(limit=settings.auth_rate_limit, window_sec=settings.auth_rate_window_sec)),
):
    tokens = await svc.register_family(body)
    set_refresh_cookie(response, tokens.refresh_token)
    return ApiResponse(data=tokens)


@router.post(
    "/login",
    response_model=ApiResponse[AuthTokensResponse],
)
async def login(
    request: Request,
    response: Response,
    body: AuthLoginRequest,
    svc: AuthService = Depends(),
    _rl: None = Depends(rate_limit_dep(limit=settings.auth_rate_limit, window_sec=settings.auth_rate_window_sec)),
):
    tokens = await svc.login(body)
    set_refresh_cookie(response, tokens.refresh_token)
    return ApiResponse(data=tokens)


@router.post("/switch-profile", response_model=ApiResponse[AuthTokensResponse])
async def switch_profile(
    response: Response,
    body: SwitchProfileRequest,
    user=Depends(get_current_user),
    svc: AuthService = Depends(),
):
    tokens = await svc.switch_profile(current_user_id=str(user.id), target_user_id=str(body.target_user_id))
    set_refresh_cookie(response, tokens.refresh_token)
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
    request: Request,
    response: Response,
    body: AuthRefreshRequest,
    svc: AuthService = Depends(),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        refresh_token = body.refresh_token

    if not refresh_token:
        raise AppError(status_code=401, code="unauthorized", message="Refresh token is missing")

    tokens = await svc.refresh(refresh_token)
    set_refresh_cookie(response, tokens.refresh_token)
    return ApiResponse(data=tokens)


@router.post("/logout", response_model=ApiResponse[dict])
async def logout(
    request: Request,
    response: Response,
    body: LogoutRequest,
    svc: AuthService = Depends(),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        refresh_token = body.refresh_token

    if refresh_token:
        await svc.logout(refresh_token)

    delete_refresh_cookie(response)
    return ApiResponse(data={"ok": True})

