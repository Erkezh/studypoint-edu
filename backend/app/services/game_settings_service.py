from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.enums import GameType
from app.models.profile import StudentProfile
from app.schemas.game_settings import GameSettingsResponse

GAME_SWITCH_COOLDOWN = timedelta(days=30)


class GameSettingsService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _response(profile: StudentProfile, now: datetime | None = None) -> GameSettingsResponse:
        now = now or GameSettingsService._now()
        next_switch = (
            profile.last_game_switch_at + GAME_SWITCH_COOLDOWN
            if profile.last_game_switch_at is not None
            else None
        )
        return GameSettingsResponse(
            active_game=profile.active_game,
            game_selected_at=profile.game_selected_at,
            last_game_switch_at=profile.last_game_switch_at,
            can_switch=next_switch is None or now >= next_switch,
            next_switch_available_at=next_switch if next_switch and now < next_switch else None,
        )

    async def _profile(self, student_id: uuid.UUID, *, lock: bool = False) -> StudentProfile:
        query = select(StudentProfile).where(StudentProfile.user_id == student_id)
        if lock:
            query = query.with_for_update()
        profile = (await self.session.execute(query)).scalar_one_or_none()
        if profile is None:
            raise AppError(status_code=404, code="profile_not_found", message="Student profile not found")
        return profile

    async def get(self, student_id: uuid.UUID) -> GameSettingsResponse:
        return self._response(await self._profile(student_id))

    async def select(self, student_id: uuid.UUID, game: GameType) -> GameSettingsResponse:
        profile = await self._profile(student_id, lock=True)
        if profile.active_game is not None:
            if profile.active_game == game:
                return self._response(profile)
            raise AppError(
                status_code=409,
                code="game_already_selected",
                message="A game is already selected. Use the switch endpoint.",
            )
        now = self._now()
        profile.active_game = game
        profile.game_selected_at = now
        await self.session.commit()
        return self._response(profile, now)

    async def switch(self, student_id: uuid.UUID, game: GameType) -> GameSettingsResponse:
        profile = await self._profile(student_id, lock=True)
        if profile.active_game is None:
            raise AppError(status_code=409, code="game_not_selected", message="Choose a game first.")
        if profile.active_game == game:
            raise AppError(status_code=409, code="game_unchanged", message="This game is already active.")

        now = self._now()
        if profile.last_game_switch_at is not None:
            next_switch = profile.last_game_switch_at + GAME_SWITCH_COOLDOWN
            if now < next_switch:
                date_label = next_switch.strftime("%Y-%m-%d")
                raise AppError(
                    status_code=409,
                    code="game_switch_cooldown",
                    message=f"You can switch games again on {date_label}.",
                    details={"next_switch_available_at": next_switch.isoformat()},
                )

        profile.active_game = game
        profile.last_game_switch_at = now
        await self.session.commit()
        return self._response(profile, now)
