from __future__ import annotations

from collections.abc import Callable
import logging

from fastapi import Depends, Request
from redis.exceptions import RedisError

from app.core.deps import get_current_user_optional, get_or_create_guest_user
from app.core.errors import AppError
from app.utils.redis import get_redis

logger = logging.getLogger(__name__)


def rate_limit_dep(*, limit: int, window_sec: int, per_user: bool = False) -> Callable:
    async def _dep(
        request: Request,
        user=Depends(get_current_user_optional) if per_user else None,
        guest_user=Depends(get_or_create_guest_user) if per_user else None,
    ):
        redis = get_redis()
        if per_user:
            # Use authenticated user if available, otherwise use guest user
            effective_user = user if user is not None else guest_user
            key = f"rl:user:{effective_user.id}:{request.url.path}"
        else:
            ip = request.client.host if request.client else "unknown"
            key = f"rl:ip:{ip}:{request.url.path}"

        try:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, window_sec)
        except RedisError as exc:
            # Fail open: auth/practice endpoints must not return 500 if Redis is read-only/unhealthy.
            logger.warning("Rate limit skipped due to Redis error: %s", exc)
            return None

        if count > limit:
            raise AppError(status_code=429, code="rate_limited", message="Too many requests")
        return None

    return _dep
