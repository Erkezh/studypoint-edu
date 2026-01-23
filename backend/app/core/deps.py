from __future__ import annotations

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import decode_token, hash_password, require_token_type
from app.db.session import get_db_session
from app.models.enums import UserRole
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
    """Optional user dependency - returns None if not authenticated (for trial questions)"""
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
    session: AsyncSession = Depends(get_db_session),
) -> "User":
    """Get or create a guest user for unauthenticated trial sessions"""
    from app.models.user import User
    
    # Try to find existing guest user
    guest_email = "guest@trial.local"
    repo = UserRepository(session)
    guest_user = await repo.get_by_email(guest_email)
    
    if guest_user is None:
        # Create guest user if it doesn't exist
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

