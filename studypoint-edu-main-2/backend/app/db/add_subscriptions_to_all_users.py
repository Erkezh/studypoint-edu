"""
Скрипт для добавления подписки всем существующим пользователям
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

from app.core.config import settings
from app.db.session import init_engine, get_sessionmaker
from app.models.user import User
from app.models.subscription import Subscription
from app.models.enums import SubscriptionPlan


async def add_subscriptions_to_all_users():
    """Добавляет активную подписку PREMIUM всем пользователям, у которых её нет"""
    # Инициализируем engine
    init_engine(settings.database_url)
    sessionmaker = get_sessionmaker()
    
    async with sessionmaker() as session:
        try:
            # Получаем всех пользователей
            stmt = select(User)
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            print(f"Найдено пользователей: {len(users)}")
            
            added_count = 0
            updated_count = 0
            
            for user in users:
                # Проверяем, есть ли у пользователя подписка
                stmt = select(Subscription).where(Subscription.user_id == user.id)
                result = await session.execute(stmt)
                subscription = result.scalar_one_or_none()
                
                if subscription is None:
                    # Создаем новую подписку PREMIUM
                    subscription = Subscription(
                        user_id=user.id,
                        plan=SubscriptionPlan.PREMIUM,
                        is_active=True,
                        active_until=None,  # Бессрочная подписка
                        provider="system",
                    )
                    session.add(subscription)
                    added_count += 1
                    print(f"Добавлена подписка для пользователя: {user.email} (ID: {user.id})")
                else:
                    # Обновляем существующую подписку, если она неактивна или не PREMIUM
                    if not subscription.is_active or subscription.plan != SubscriptionPlan.PREMIUM:
                        subscription.plan = SubscriptionPlan.PREMIUM
                        subscription.is_active = True
                        subscription.active_until = None  # Бессрочная подписка
                        subscription.provider = "system"
                        updated_count += 1
                        print(f"Обновлена подписка для пользователя: {user.email} (ID: {user.id})")
            
            await session.commit()
            print(f"\nГотово!")
            print(f"Добавлено подписок: {added_count}")
            print(f"Обновлено подписок: {updated_count}")
            print(f"Всего обработано пользователей: {len(users)}")
            
        except Exception as e:
            await session.rollback()
            print(f"Ошибка: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(add_subscriptions_to_all_users())
