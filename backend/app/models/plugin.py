from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Plugin(Base, TimestampMixin):
    """Модель плагина для интерактивных заданий.
    
    Плагины изолированы от основного приложения и загружаются через админку.
    Каждый плагин имеет версию и хранится в отдельной директории.
    """
    __tablename__ = "plugins"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)  # UUID как строка для уникальности записи в БД
    plugin_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # ID из manifest (для пути к файлам)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    entry: Mapped[str] = mapped_column(String(255), nullable=False)  # index.html или другой entry point
    api_version: Mapped[str] = mapped_column(String(16), nullable=False, server_default="1")
    capabilities: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False, server_default="{}")
    height: Mapped[int] = mapped_column(Integer, nullable=False, server_default="400")  # Высота iframe в пикселях
    is_published: Mapped[bool] = mapped_column(nullable=False, server_default="false")  # Опубликован ли плагин для студентов
    manifest_data: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False, server_default="{}")  # Полный manifest для справки
