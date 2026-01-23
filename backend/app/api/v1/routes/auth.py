from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.core.config import settings
from app.core.rate_limit import rate_limit_dep
from app.schemas.auth import (
    AuthLoginRequest,
    AuthRefreshRequest,
    AuthRegisterRequest,
    AuthTokensResponse,
    LogoutRequest,
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

