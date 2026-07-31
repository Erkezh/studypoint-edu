from __future__ import annotations

import uuid

from fastapi import Depends, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import decode_token, hash_password, require_token_type
from app.db.session import get_db_session
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repo import UserRepository

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_db_session),
):
    if creds is None:
        raise AppError(status_code=401, code="unauthorized", message="Missing bearer token")
    payload = decode_token(creds.credentials)
    require_token_type(payload, "access")
    user_id = payload.get("sub")
    if not user_id:
        raise AppError(status_code=401, code="unauthorized", message="Invalid token subject")
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise AppError(status_code=401, code="unauthorized", message="User not found or inactive")
    return user


async def get_current_user_optional(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_db_session),
):
    """Optional user dependency - returns None when credentials are absent, invalid or expired."""
    if creds is None:
        return None
    try:
        payload = decode_token(creds.credentials)
        require_token_type(payload, "access")
        user_id = payload.get("sub")
        if not user_id:
            return None
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)
        if user is None or not user.is_active:
            return None
        return user
    except Exception:
        return None


async def get_or_create_guest_user(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """Get or create a unique guest user per session/cookie to isolate unauthenticated practice sessions."""

    # Retrieve guest_id from header X-Guest-ID or cookie guest_id
    guest_id = request.headers.get("X-Guest-ID") or request.cookies.get("guest_id")

    if not guest_id or len(guest_id) < 8:
        guest_id = uuid.uuid4().hex
        response.set_cookie(
            key="guest_id",
            value=guest_id,
            max_age=86400,  # 24 hours
            httponly=True,
            samesite="lax",
        )

    guest_email = f"guest_{guest_id[:16]}@trial.local"
    repo = UserRepository(session)
    guest_user = await repo.get_by_email(guest_email)

    if guest_user is None:
        guest_user = User(
            id=uuid.uuid4(),
            email=guest_email,
            password_hash=hash_password("guest_password_not_used"),
            full_name="Guest User",
            role=UserRole.STUDENT,
            is_active=True,
        )
        session.add(guest_user)
        await session.flush()

    return guest_user
