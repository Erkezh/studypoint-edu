from __future__ import annotations

import pytest
from asgi_lifespan import LifespanManager


@pytest.mark.asyncio
async def test_health_endpoints_report_live_and_ready(client):
    live = await client.get("/api/v1/health/live")
    assert live.status_code == 200, live.text
    assert live.json()["data"]["status"] == "live"

    ready = await client.get("/api/v1/health/ready")
    assert ready.status_code == 200, ready.text
    assert ready.json()["data"]["status"] == "ready"
    assert ready.json()["data"]["checks"] == {"database": "ok", "redis": "ok"}


@pytest.mark.asyncio
async def test_health_ready_returns_503_when_database_check_fails(client, monkeypatch):
    from app.api.v1.routes import health as health_routes
    from app.services.health_service import DependencyNotReadyError

    async def fail_database() -> dict[str, str]:
        raise DependencyNotReadyError("database", "Database not ready")

    monkeypatch.setattr(health_routes, "get_readiness_checks", fail_database)

    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 503, response.text
    assert response.json()["error"]["message"] == "Database not ready"
    assert response.json()["error"]["details"] == {"service": "database"}


@pytest.mark.asyncio
async def test_health_ready_returns_503_when_redis_check_fails(client, monkeypatch):
    from app.api.v1.routes import health as health_routes
    from app.services.health_service import DependencyNotReadyError

    async def fail_redis() -> dict[str, str]:
        raise DependencyNotReadyError("redis", "Redis not ready")

    monkeypatch.setattr(health_routes, "get_readiness_checks", fail_redis)

    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 503, response.text
    assert response.json()["error"]["message"] == "Redis not ready"
    assert response.json()["error"]["details"] == {"service": "redis"}


@pytest.mark.asyncio
async def test_lifespan_aborts_when_database_preflight_fails(monkeypatch):
    from app import main as main_module

    async def fail_readiness() -> dict[str, str]:
        raise RuntimeError("password authentication failed for user 'postgres'")

    monkeypatch.setattr(main_module, "get_readiness_checks", fail_readiness)

    with pytest.raises(RuntimeError, match="password authentication failed"):
        async with LifespanManager(main_module.app):
            pass
