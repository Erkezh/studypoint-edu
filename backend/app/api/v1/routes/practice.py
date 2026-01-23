from __future__ import annotations

from fastapi import APIRouter, Depends, Header

from app.core.config import settings
from app.core.deps import get_current_user, get_current_user_optional, get_or_create_guest_user
from app.core.idempotency import idempotency_get, idempotency_set
from app.core.rate_limit import rate_limit_dep
from app.schemas.base import ApiResponse
from app.schemas.practice import (
    PracticeHeartbeatRequest,
    PracticeSessionCreateRequest,
    PracticeSessionResponse,
    PracticeSubmitRequest,
    PracticeSubmitResponse,
)
from app.services.practice_service import PracticeService

router = APIRouter()


@router.post("/sessions", response_model=ApiResponse[PracticeSessionResponse])
async def create_session(
    body: PracticeSessionCreateRequest,
    user=Depends(get_current_user_optional),
    guest_user=Depends(get_or_create_guest_user),
    svc: PracticeService = Depends(),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    # Use authenticated user if available, otherwise use guest user for trial sessions
    effective_user = user if user is not None else guest_user
    user_id_for_cache = effective_user.id
    
    cached = await idempotency_get(user_id=user_id_for_cache, key=idempotency_key, request_body=body)
    if cached is not None:
        return cached
    result = await svc.start_session(user_id=effective_user.id, skill_id=body.skill_id)
    resp = ApiResponse(data=result)
    await idempotency_set(user_id=user_id_for_cache, key=idempotency_key, request_body=body, response=resp)
    return resp


@router.get("/sessions/{session_id}", response_model=ApiResponse[PracticeSessionResponse])
async def get_session(
    session_id: str,
    user=Depends(get_current_user_optional),
    guest_user=Depends(get_or_create_guest_user),
    svc: PracticeService = Depends(),
):
    effective_user = user if user is not None else guest_user
    return ApiResponse(data=await svc.get_session(user_id=effective_user.id, session_id=session_id))


@router.post("/sessions/{session_id}/next", response_model=ApiResponse[dict])
async def next_question(
    session_id: str,
    user=Depends(get_current_user_optional),
    guest_user=Depends(get_or_create_guest_user),
    svc: PracticeService = Depends(),
):
    effective_user = user if user is not None else guest_user
    return ApiResponse(data=await svc.next_question(user_id=effective_user.id, session_id=session_id))


@router.post("/sessions/{session_id}/submit", response_model=ApiResponse[PracticeSubmitResponse])
async def submit_answer(
    session_id: str,
    body: PracticeSubmitRequest,
    user=Depends(get_current_user_optional),
    guest_user=Depends(get_or_create_guest_user),
    svc: PracticeService = Depends(),
    _rl: None = Depends(rate_limit_dep(limit=settings.submit_rate_limit, window_sec=settings.submit_rate_window_sec, per_user=True)),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    effective_user = user if user is not None else guest_user
    cached = await idempotency_get(user_id=effective_user.id, key=idempotency_key, request_body=body)
    if cached is not None:
        return cached
    result = await svc.submit(user_id=effective_user.id, session_id=session_id, req=body)
    resp = ApiResponse(data=result)
    await idempotency_set(user_id=effective_user.id, key=idempotency_key, request_body=body, response=resp)
    return resp


@router.post("/sessions/{session_id}/finish", response_model=ApiResponse[dict])
async def finish(
    session_id: str,
    user=Depends(get_current_user_optional),
    guest_user=Depends(get_or_create_guest_user),
    svc: PracticeService = Depends(),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    effective_user = user if user is not None else guest_user
    cached = await idempotency_get(user_id=effective_user.id, key=idempotency_key, request_body={"session_id": session_id})
    if cached is not None:
        return cached
    await svc.finish(user_id=effective_user.id, session_id=session_id)
    resp = ApiResponse(data={"ok": True})
    await idempotency_set(user_id=effective_user.id, key=idempotency_key, request_body={"session_id": session_id}, response=resp)
    return resp


@router.post("/sessions/{session_id}/heartbeat", response_model=ApiResponse[PracticeSessionResponse])
async def heartbeat(
    session_id: str,
    body: PracticeHeartbeatRequest,
    user=Depends(get_current_user_optional),
    guest_user=Depends(get_or_create_guest_user),
    svc: PracticeService = Depends(),
):
    # We currently only use server-time based updates; client fields are accepted for future tuning.
    effective_user = user if user is not None else guest_user
    return ApiResponse(data=await svc.heartbeat(user_id=effective_user.id, session_id=session_id))
