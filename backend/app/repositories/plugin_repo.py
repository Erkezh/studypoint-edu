from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plugin import Plugin


class PluginRepository:
    """Репозиторий для работы с плагинами в БД."""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, plugin_uuid: str) -> Plugin | None:
        """Получить плагин по UUID (id в БД)."""
        stmt = select(Plugin).where(Plugin.id == plugin_uuid)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_plugin_id(self, plugin_id: str) -> Plugin | None:
        """Получить плагин по plugin_id (из manifest)."""
        stmt = select(Plugin).where(Plugin.plugin_id == plugin_id).order_by(Plugin.created_at.desc())
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_plugin_id_and_version(self, plugin_id: str, version: str) -> Plugin | None:
        """Получить плагин по plugin_id и версии."""
        stmt = select(Plugin).where(Plugin.plugin_id == plugin_id, Plugin.version == version)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_all(self) -> list[Plugin]:
        """Получить список всех плагинов."""
        stmt = select(Plugin).order_by(Plugin.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, plugin_data: dict) -> Plugin:
        """Создать новый плагин."""
        plugin = Plugin(**plugin_data)
        self.session.add(plugin)
        await self.session.flush()
        return plugin

    async def update_published(self, plugin_id: str, is_published: bool) -> Plugin | None:
        """Обновить статус публикации плагина."""
        plugin = await self.get_by_id(plugin_id)
        if plugin:
            plugin.is_published = is_published
            await self.session.flush()
        return plugin

    async def delete(self, plugin_id: str) -> bool:
        """Удалить плагин по UUID (id в БД)."""
        plugin = await self.get_by_id(plugin_id)
        if plugin:
            await self.session.delete(plugin)
            await self.session.flush()
            return True
        return False
