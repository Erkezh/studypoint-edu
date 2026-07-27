from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import GameType


class GameSelectionRequest(BaseModel):
    game: GameType


class GameSettingsResponse(BaseModel):
    active_game: GameType | None
    game_selected_at: datetime | None
    last_game_switch_at: datetime | None
    can_switch: bool
    next_switch_available_at: datetime | None
