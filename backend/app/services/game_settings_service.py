from __future__ import annotations

from datetime import datetime, timezone
import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.enums import GameType
from app.models.profile import StudentProfile
from app.schemas.game_settings import GameSettingsResponse

class GameSettingsService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _response(profile: StudentProfile) -> GameSettingsResponse:
        return GameSettingsResponse(
            active_game=profile.active_game,
            game_selected_at=profile.game_selected_at,
            last_game_switch_at=profile.last_game_switch_at,
            can_switch=False,
            next_switch_available_at=None,
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
                message="Your game has already been selected and cannot be changed.",
            )
        now = self._now()
        profile.active_game = game
        profile.game_selected_at = now
        await self.session.commit()
        return self._response(profile)

    async def switch(self, student_id: uuid.UUID, game: GameType) -> GameSettingsResponse:
        profile = await self._profile(student_id, lock=True)
        if profile.active_game is None:
            raise AppError(status_code=409, code="game_not_selected", message="Choose a game first.")
        raise AppError(
            status_code=409,
            code="game_selection_locked",
            message="Your first game choice is permanent and cannot be changed.",
        )
