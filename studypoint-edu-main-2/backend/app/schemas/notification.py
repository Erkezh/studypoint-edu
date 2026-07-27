from __future__ import annotations

from datetime import datetime
import uuid

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
