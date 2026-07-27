from __future__ import annotations

import asyncio
import os

import pytest
from alembic import command
from alembic.config import Config
from asgi_lifespan import LifespanManager
import httpx
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


def _set_test_env() -> None:
    os.environ.setdefault("APP_NAME", "IXL Clone API (test)")
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("API_V1_PREFIX", "/api/v1")
    os.environ.setdefault("JWT_ISSUER", "ixl-clone")
    os.environ.setdefault("JWT_AUDIENCE", "ixl-clone-users")
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
    os.environ.setdefault("JWT_ACCESS_TTL_SEC", "900")
    os.environ.setdefault("JWT_REFRESH_TTL_SEC", "2592000")
    os.environ.setdefault("PASSWORD_HASH_SCHEME", "argon2")

    # Default to local services; override via env if running under Docker/network.
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/ixl")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

    os.environ.setdefault("CACHE_TTL_SEC", "1")
    os.environ.setdefault("AUTH_RATE_LIMIT", "1000")
    os.environ.setdefault("SUBMIT_RATE_LIMIT", "1000")
    os.environ.setdefault("FREE_DAILY_QUESTION_LIMIT", "100000")


_set_test_env()


@pytest.fixture(scope="session", autouse=True)
def migrate_and_seed() -> None:
    async def _reset_db() -> None:
        from app.core.config import settings

        engine = create_async_engine(settings.database_url)
        async with engine.begin() as conn:
            await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
            await conn.execute(text("CREATE SCHEMA public;"))
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
        await engine.dispose()

    asyncio.run(_reset_db())
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    from app.db.seed import seed

    asyncio.run(seed())


@pytest.fixture(scope="session", autouse=True)
def flush_redis() -> None:
    async def _run() -> None:
        from app.core.config import settings

        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        await redis.flushdb()
        await redis.aclose()

    asyncio.run(_run())


@pytest.fixture
async def client() -> httpx.AsyncClient:
    from app.main import app

    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.fixture
async def cleanup_practice_tables() -> None:
    from app.core.config import settings

    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE practice_attempts, practice_sessions, progress_snapshots RESTART IDENTITY CASCADE;"))
    await engine.dispose()


async def login(client: httpx.AsyncClient, email: str, password: str) -> dict:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


@pytest.fixture
async def admin_token(client: httpx.AsyncClient) -> str:
    data = await login(client, "admin@example.com", "Password123!")
    return data["access_token"]


@pytest.fixture
async def student_token(client: httpx.AsyncClient) -> str:
    data = await login(client, "student@example.com", "Password123!")
    return data["access_token"]
