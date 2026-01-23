from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.errors import AppError


pwd_context = CryptContext(schemes=[settings.password_hash_scheme], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


def _now() -> int:
    return int(time.time())


def create_access_token(*, user_id: str, role: str) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    payload = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": user_id,
        "role": role,
        "type": "access",
        "jti": jti,
        "iat": _now(),
        "exp": _now() + settings.jwt_access_ttl_sec,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256"), jti


def create_refresh_token(*, user_id: str, role: str) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    payload = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": user_id,
        "role": role,
        "type": "refresh",
        "jti": jti,
        "iat": _now(),
        "exp": _now() + settings.jwt_refresh_ttl_sec,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256"), jti


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
    except JWTError as e:
        raise AppError(status_code=401, code="unauthorized", message="Invalid token") from e


def require_token_type(payload: dict[str, Any], token_type: str) -> None:
    if payload.get("type") != token_type:
        raise AppError(status_code=401, code="unauthorized", message="Invalid token type")

