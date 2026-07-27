from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GarageSaveRequest(BaseModel):
    selection: dict[str, Any] = Field(default_factory=dict)


class GarageRandomizeRequest(BaseModel):
    selection: dict[str, Any] = Field(default_factory=dict)


class GarageSelectionResponse(BaseModel):
    selection: dict[str, Any]
    savedOffline: bool = False
