from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def init_engine(
    database_url: str,
    *,
    pool_size: int = 20,
    max_overflow: int = 20,
    pool_timeout_sec: int = 30,
    pool_recycle_sec: int = 1800,
    connect_timeout_sec: int = 10,
    command_timeout_sec: int = 30,
) -> None:
    global _engine, _sessionmaker
    engine_kwargs: dict[str, object] = {"pool_pre_ping": True}

    if database_url.startswith("postgresql"):
        engine_kwargs.update(
            {
                "pool_size": pool_size,
                "max_overflow": max_overflow,
                "pool_timeout": pool_timeout_sec,
                "pool_recycle": pool_recycle_sec,
                "pool_use_lifo": True,
                "connect_args": {
                    "timeout": connect_timeout_sec,
                    "command_timeout": command_timeout_sec,
                },
            }
        )

    _engine = create_async_engine(database_url, **engine_kwargs)
    _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)


async def close_engine() -> None:
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
    _sessionmaker = None


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Database engine not initialized")
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    if _sessionmaker is None:
        raise RuntimeError("Sessionmaker not initialized")
    return _sessionmaker


async def ping_database() -> None:
    engine = get_engine()
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        async with session.begin():
            yield session
