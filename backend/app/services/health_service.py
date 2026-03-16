from __future__ import annotations

import logging

from app.db.session import ping_database
from app.utils.redis import ping_redis

logger = logging.getLogger(__name__)


class DependencyNotReadyError(RuntimeError):
    def __init__(self, service: str, message: str) -> None:
        super().__init__(message)
        self.service = service


async def get_readiness_checks() -> dict[str, str]:
    try:
        await ping_database()
    except Exception as exc:
        logger.exception("Database readiness check failed: %s", exc)
        raise DependencyNotReadyError("database", "Database not ready") from exc

    try:
        await ping_redis()
    except Exception as exc:
        logger.exception("Redis readiness check failed: %s", exc)
        raise DependencyNotReadyError("redis", "Redis not ready") from exc

    return {
        "database": "ok",
        "redis": "ok",
    }
