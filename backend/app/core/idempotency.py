from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel

from app.schemas.base import ApiResponse
from app.utils.redis import get_redis


def _request_hash(body: Any) -> str:
    if isinstance(body, BaseModel):
        raw = body.model_dump_json()
    else:
        raw = json.dumps(body, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def idempotency_get(*, user_id: str, key: str | None, request_body: Any) -> ApiResponse | None:
    if not key:
        return None
    redis = get_redis()
    redis_key = f"idem:{user_id}:{key}"
    stored = await redis.get(redis_key)
    if not stored:
        return None
    payload = json.loads(stored)
    if payload.get("request_hash") != _request_hash(request_body):
        return None
    return ApiResponse.model_validate(payload["response"])


async def idempotency_set(
    *,
    user_id: str,
    key: str | None,
    request_body: Any,
    response: ApiResponse,
    ttl_sec: int = 60 * 60 * 24,
) -> None:
    if not key:
        return None
    redis = get_redis()
    redis_key = f"idem:{user_id}:{key}"
    payload = {
        "request_hash": _request_hash(request_body),
        "response": response.model_dump(mode="json"),
    }
    await redis.setex(redis_key, ttl_sec, json.dumps(payload))

