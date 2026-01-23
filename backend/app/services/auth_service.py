from __future__ import annotations

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.core.security import (
    TokenPair,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    require_token_type,
    verify_password,
)
from app.db.session import get_db_session
from app.models.enums import SubscriptionPlan, UserRole
from app.models.profile import StudentProfile
from app.models.subscription import Subscription
from app.repositories.user_repo import UserRepository
from app.schemas.auth import AuthLoginRequest, AuthRegisterRequest, AuthTokensResponse
from app.schemas.user import StudentProfileResponse, SubscriptionResponse, UserMeResponse
from app.utils.redis import get_redis


class AuthService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def _issue_tokens(self, *, user_id: str, role: str) -> TokenPair:
        access, _ = create_access_token(user_id=user_id, role=role)
        refresh, refresh_jti = create_refresh_token(user_id=user_id, role=role)
        redis = get_redis()
        await redis.setex(f"auth:refresh:{refresh_jti}", settings.jwt_refresh_ttl_sec, user_id)
        return TokenPair(access_token=access, refresh_token=refresh)

    async def register(self, req: AuthRegisterRequest) -> AuthTokensResponse:
        if req.role not in {UserRole.STUDENT, UserRole.PARENT}:
            raise AppError(status_code=403, code="forbidden", message="Cannot self-register for this role")

        try:
            user = await self.users.create(
                email=req.email,
                password_hash=hash_password(req.password),
                full_name=req.full_name,
                role=req.role,
            )
            self.session.add(StudentProfile(user_id=user.id, grade_level=req.grade_level, school=req.school))
            self.session.add(Subscription(user_id=user.id, plan=SubscriptionPlan.FREE, is_active=True))
            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Email already registered") from e

        tokens = await self._issue_tokens(user_id=str(user.id), role=user.role.value)
        return AuthTokensResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            user=UserMeResponse(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                profile=StudentProfileResponse(grade_level=req.grade_level, school=req.school),
                subscription=SubscriptionResponse(plan=SubscriptionPlan.FREE, is_active=True),
            ),
        )

    async def login(self, req: AuthLoginRequest) -> AuthTokensResponse:
        user = await self.users.get_by_email(str(req.email))
        if user is None or not user.is_active or not verify_password(req.password, user.password_hash):
            raise AppError(status_code=401, code="unauthorized", message="Invalid credentials")
        tokens = await self._issue_tokens(user_id=str(user.id), role=user.role.value)
        sub = await self.users.get_subscription(user.id)
        profile = user.profile
        return AuthTokensResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            user=UserMeResponse(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                profile=StudentProfileResponse(grade_level=profile.grade_level, school=profile.school) if profile else None,
                subscription=SubscriptionResponse(plan=sub.plan, is_active=sub.is_active) if sub else None,
            ),
        )

    async def refresh(self, refresh_token: str) -> AuthTokensResponse:
        payload = decode_token(refresh_token)
        require_token_type(payload, "refresh")
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if not user_id or not jti:
            raise AppError(status_code=401, code="unauthorized", message="Invalid refresh token")

        redis = get_redis()
        stored_user = await redis.get(f"auth:refresh:{jti}")
        if stored_user != user_id:
            raise AppError(status_code=401, code="unauthorized", message="Refresh token revoked")

        await redis.delete(f"auth:refresh:{jti}")
        user = await self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AppError(status_code=401, code="unauthorized", message="User not found or inactive")

        tokens = await self._issue_tokens(user_id=str(user.id), role=user.role.value)
        sub = await self.users.get_subscription(user.id)
        profile = user.profile
        return AuthTokensResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            user=UserMeResponse(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                profile=StudentProfileResponse(grade_level=profile.grade_level, school=profile.school) if profile else None,
                subscription=SubscriptionResponse(plan=sub.plan, is_active=sub.is_active) if sub else None,
            ),
        )

    async def logout(self, refresh_token: str) -> None:
        payload = decode_token(refresh_token)
        require_token_type(payload, "refresh")
        jti = payload.get("jti")
        if jti:
            redis = get_redis()
            await redis.delete(f"auth:refresh:{jti}")
