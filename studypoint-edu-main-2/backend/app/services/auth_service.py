from __future__ import annotations

import logging

from fastapi import Depends
from redis.exceptions import RedisError
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
from app.schemas.auth import AuthLoginRequest, AuthRegisterRequest, AuthRegisterFamilyRequest, AuthTokensResponse
from app.schemas.user import StudentProfileResponse, SubscriptionResponse, UserMeResponse
from app.utils.redis import get_redis

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def _issue_tokens(self, *, user_id: str, role: str) -> TokenPair:
        access, _ = create_access_token(user_id=user_id, role=role)
        refresh, refresh_jti = create_refresh_token(user_id=user_id, role=role)
        try:
            redis = get_redis()
            await redis.setex(f"auth:refresh:{refresh_jti}", settings.jwt_refresh_ttl_sec, user_id)
        except RedisError as exc:
            # Keep login/register available even when Redis is temporarily read-only.
            logger.warning("Failed to persist refresh token in Redis: %s", exc)
        return TokenPair(access_token=access, refresh_token=refresh)

    async def register(self, req: AuthRegisterRequest) -> AuthTokensResponse:
        if req.role not in {UserRole.STUDENT, UserRole.PARENT, UserRole.TEACHER}:
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

    async def register_family(self, req: AuthRegisterFamilyRequest) -> AuthTokensResponse:
        try:
            # 1. Create Parent
            parent_user = await self.users.create(
                email=req.parent_email,
                password_hash=hash_password(req.parent_password),
                full_name=req.parent_name,
                role=UserRole.PARENT,
            )
            # Add free subscription to Parent (so it has something active)
            self.session.add(Subscription(user_id=parent_user.id, plan=SubscriptionPlan.FAMILY, is_active=True))

            # 2. Create Children
            for child in req.children:
                # generate artificial sibling email since email is unique and required
                import uuid
                child_email = f"child_{uuid.uuid4().hex[:8]}@{req.parent_email.split('@')[-1]}"
                
                child_user = await self.users.create(
                    email=child_email,
                    password_hash=parent_user.password_hash,  # Parent password access for now, but usually accessed via switch
                    full_name=child.name,
                    role=UserRole.STUDENT
                )
                child_user.parent_id = parent_user.id
                
                self.session.add(StudentProfile(user_id=child_user.id, grade_level=child.grade_level))
                self.session.add(Subscription(user_id=child_user.id, plan=SubscriptionPlan.FAMILY, is_active=True))

            await self.session.flush()
        except IntegrityError as e:
            raise AppError(status_code=409, code="conflict", message="Email already registered or error during family creation") from e
            
        # Refetch Parent to ensure relationship is solid
        parent_user = await self.users.get_by_id(parent_user.id)

        # Login as Parent initially
        tokens = await self._issue_tokens(user_id=str(parent_user.id), role=parent_user.role.value)
        sub = await self.users.get_subscription(parent_user.id)
        
        return AuthTokensResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            user=UserMeResponse(
                id=str(parent_user.id),
                email=parent_user.email,
                full_name=parent_user.full_name,
                role=parent_user.role,
                is_active=parent_user.is_active,
                profile=None,
                subscription=SubscriptionResponse(plan=sub.plan, is_active=sub.is_active) if sub else None,
                parent_id=None,
            ),
        )

    async def login(self, req: AuthLoginRequest) -> AuthTokensResponse:
        user = await self.users.get_by_email(str(req.email))
        if user is None:
            logger.warning("LOGIN FAIL: user not found for email/username=%s", req.email)
            raise AppError(status_code=401, code="unauthorized", message="Invalid credentials")
        if not user.is_active:
            logger.warning("LOGIN FAIL: user %s is inactive", req.email)
            raise AppError(status_code=401, code="unauthorized", message="Invalid credentials")
        if not verify_password(req.password, user.password_hash):
            logger.warning("LOGIN FAIL: wrong password for user %s (hash starts with: %s)", req.email, user.password_hash[:20] if user.password_hash else "NONE")
            raise AppError(status_code=401, code="unauthorized", message="Invalid credentials")
        logger.info("LOGIN OK: user %s role=%s", req.email, user.role)
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
                parent_id=str(user.parent_id) if getattr(user, 'parent_id', None) else None,
            ),
        )

    async def refresh(self, refresh_token: str) -> AuthTokensResponse:
        payload = decode_token(refresh_token)
        require_token_type(payload, "refresh")
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if not user_id or not jti:
            raise AppError(status_code=401, code="unauthorized", message="Invalid refresh token")

        try:
            redis = get_redis()
            stored_user = await redis.get(f"auth:refresh:{jti}")
        except RedisError as exc:
            raise AppError(
                status_code=503,
                code="service_unavailable",
                message="Authentication storage temporarily unavailable",
            ) from exc
        if stored_user != user_id:
            raise AppError(status_code=401, code="unauthorized", message="Refresh token revoked")

        try:
            await redis.delete(f"auth:refresh:{jti}")
        except RedisError as exc:
            raise AppError(
                status_code=503,
                code="service_unavailable",
                message="Authentication storage temporarily unavailable",
            ) from exc
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
                parent_id=str(user.parent_id) if getattr(user, 'parent_id', None) else None,
            ),
        )

    async def switch_profile(self, current_user_id: str, target_user_id: str) -> AuthTokensResponse:
        current_user = await self.users.get_by_id(current_user_id)
        target_user = await self.users.get_by_id(target_user_id)

        if not current_user or not target_user:
            raise AppError(status_code=404, code="not_found", message="User not found")

        # Verify they belong to the same family
        # Valid family moves:
        # parent -> child (target child.parent_id == current parent.id)
        # child -> parent (current child.parent_id == target parent.id)
        # child -> child (current child.parent_id == target child.parent_id)
        is_valid = False
        if current_user.role == UserRole.PARENT and getattr(target_user, 'parent_id', None) == current_user.id:
            is_valid = True
        elif target_user.role == UserRole.PARENT and getattr(current_user, 'parent_id', None) == target_user.id:
            is_valid = True
        # Both are children of the same parent
        elif getattr(current_user, 'parent_id', None) and getattr(current_user, 'parent_id', None) == getattr(target_user, 'parent_id', None):
            is_valid = True
        elif current_user.id == target_user.id:
            is_valid = True

        if not is_valid:
            raise AppError(status_code=403, code="forbidden", message="Cannot access this profile")

        # issue tokens for target user
        tokens = await self._issue_tokens(user_id=str(target_user.id), role=target_user.role.value)
        sub = await self.users.get_subscription(target_user.id)
        profile = getattr(target_user, 'profile', None)
        
        return AuthTokensResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            user=UserMeResponse(
                id=str(target_user.id),
                email=target_user.email,
                full_name=target_user.full_name,
                role=target_user.role,
                is_active=target_user.is_active,
                profile=StudentProfileResponse(grade_level=profile.grade_level, school=profile.school) if profile else None,
                subscription=SubscriptionResponse(plan=sub.plan, is_active=sub.is_active) if sub else None,
                parent_id=str(target_user.parent_id) if getattr(target_user, 'parent_id', None) else None,
            ),
        )

    async def get_family_members(self, current_user) -> list[dict]:
        # Determine the parent ID
        parent_id = current_user.id if current_user.role == UserRole.PARENT else getattr(current_user, 'parent_id', None)
        if not parent_id:
            return []

        # Fetch parent
        parent = await self.users.get_by_id(parent_id)
        # Fetch children
        children = await self.users.get_children_by_parent_id(parent_id)

        members = []
        if parent:
            members.append({
                "id": parent.id,
                "full_name": parent.full_name,
                "role": parent.role,
                "grade_level": None,
                "is_current": parent.id == current_user.id
            })

        for child in children:
            members.append({
                "id": child.id,
                "full_name": child.full_name,
                "role": child.role,
                "grade_level": child.profile.grade_level if child.profile else None,
                "is_current": child.id == current_user.id
            })

        return members

    async def logout(self, refresh_token: str) -> None:
        payload = decode_token(refresh_token)
        require_token_type(payload, "refresh")
        jti = payload.get("jti")
        if jti:
            try:
                redis = get_redis()
                await redis.delete(f"auth:refresh:{jti}")
            except RedisError as exc:
                # Logout should remain best-effort and never crash on Redis state issues.
                logger.warning("Failed to revoke refresh token in Redis during logout: %s", exc)
