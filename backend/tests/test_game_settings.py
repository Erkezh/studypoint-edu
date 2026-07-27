from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def _reset_game_settings(last_switch: datetime | None = None, active_game: str | None = None) -> None:
    from app.core.config import settings

    engine = create_async_engine(settings.database_url)
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                UPDATE student_profiles
                SET active_game = CAST(:active_game AS game_type),
                    game_selected_at = CASE WHEN :active_game IS NULL THEN NULL ELSE now() END,
                    last_game_switch_at = :last_switch
                WHERE user_id = (SELECT id FROM users WHERE email = 'student@example.com')
                """
            ),
            {"active_game": active_game, "last_switch": last_switch},
        )
    await engine.dispose()


@pytest.fixture(autouse=True)
async def reset_student_game() -> None:
    await _reset_game_settings()
    yield
    await _reset_game_settings()


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_first_selection_is_free_idempotent_and_preserves_wallet(client, student_token):
    before = (await client.get("/api/v1/gamification/wallet", headers=auth(student_token))).json()["data"]
    selected = await client.post("/api/v1/me/game-settings/select", json={"game": "car"}, headers=auth(student_token))
    duplicate = await client.post("/api/v1/me/game-settings/select", json={"game": "car"}, headers=auth(student_token))
    after = (await client.get("/api/v1/gamification/wallet", headers=auth(student_token))).json()["data"]

    assert selected.status_code == 200
    assert duplicate.status_code == 200
    assert selected.json()["data"]["active_game"] == "car"
    assert selected.json()["data"]["last_game_switch_at"] is None
    assert {key: after[key] for key in ("coins", "xp", "level")} == {key: before[key] for key in ("coins", "xp", "level")}


async def test_invalid_game_is_rejected(client, student_token):
    response = await client.post("/api/v1/me/game-settings/select", json={"game": "spaceship"}, headers=auth(student_token))
    assert response.status_code == 422


async def test_game_settings_require_authentication_and_student_role(client, admin_token):
    assert (await client.get("/api/v1/me/game-settings")).status_code == 401
    assert (await client.get("/api/v1/me/game-settings", headers=auth(admin_token))).status_code == 403


async def test_switch_rejects_same_game_and_preserves_progress(client, student_token):
    await client.post("/api/v1/me/game-settings/select", json={"game": "car"}, headers=auth(student_token))
    before = (await client.get("/api/v1/gamification/wallet", headers=auth(student_token))).json()["data"]
    same = await client.post("/api/v1/me/game-settings/switch", json={"game": "car"}, headers=auth(student_token))
    switched = await client.post("/api/v1/me/game-settings/switch", json={"game": "character"}, headers=auth(student_token))
    after = (await client.get("/api/v1/gamification/wallet", headers=auth(student_token))).json()["data"]

    assert same.status_code == 409
    assert switched.status_code == 200
    assert switched.json()["data"]["active_game"] == "character"
    assert switched.json()["data"]["can_switch"] is False
    assert {key: after[key] for key in ("coins", "xp", "level")} == {key: before[key] for key in ("coins", "xp", "level")}


async def test_switch_cooldown_is_enforced_and_expires(client, student_token):
    await _reset_game_settings(datetime.now(timezone.utc) - timedelta(days=29), "car")
    blocked = await client.post("/api/v1/me/game-settings/switch", json={"game": "character"}, headers=auth(student_token))
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "game_switch_cooldown"

    await _reset_game_settings(datetime.now(timezone.utc) - timedelta(days=31), "car")
    allowed = await client.post("/api/v1/me/game-settings/switch", json={"game": "character"}, headers=auth(student_token))
    assert allowed.status_code == 200
    assert allowed.json()["data"]["active_game"] == "character"
