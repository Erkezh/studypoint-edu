import asyncio
from app.utils.redis import init_redis, close_redis
from app.services.presence_service import update_presence, get_active_students
from app.core.config import settings

async def main():
    await init_redis(settings.redis_url)
    user_id = "00000000-0000-0000-0000-000000000000"
    
    await update_presence(
        user_id=user_id,
        skill_id=1,
        skill_name="Test Skill",
        smartscore=50,
        correct=5,
        wrong=0,
        questions_answered=5,
        session_id="session123"
    )
    print("Updated presence")
    
    active = await get_active_students([user_id])
    print(f"Active students: {active}")
    await close_redis()

if __name__ == "__main__":
    asyncio.run(main())
