from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends

from app.core.deps import get_current_user
from app.core.errors import AppError


def require_roles(*roles: str) -> Callable:
    async def _dep(user=Depends(get_current_user)):
        role_value = getattr(user.role, "value", user.role)
        if role_value not in roles:
            raise AppError(status_code=403, code="forbidden", message="Insufficient permissions")
        return None

    return _dep
