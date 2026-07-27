from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedMeta(BaseModel):
    page: int
    page_size: int
    total: int


class ApiResponse(BaseModel, Generic[T]):
    data: T | None = None
    meta: Any | None = Field(default=None, examples=[{"page": 1, "page_size": 20, "total": 123}])

