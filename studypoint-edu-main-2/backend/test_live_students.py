import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.utils.redis import init_redis, close_redis
from app.services.presence_service import get_active_students
from app.core.config import settings

async def main():
    await init_redis(settings.redis_url)
    async with AsyncSessionLocal() as session:
        # Find a teacher
        stmt = select(User).where(User.role == UserRole.TEACHER).limit(1)
        teacher = (await session.execute(stmt)).scalar_one_or_none()
        if not teacher:
            print("No teacher found")
            return
        
        print(f"Testing for teacher: {teacher.full_name} ({teacher.id})")
        
        # Get their students
        stmt = select(User.id, User.full_name).where(User.teacher_id == teacher.id)
        rows = (await session.execute(stmt)).all()
        student_ids = [str(row.id) for row in rows]
        print(f"Found {len(student_ids)} students")
        
        if student_ids:
            active = await get_active_students(student_ids)
            print(f"Active students from DB mapping: {active}")
            
    await close_redis()

if __name__ == "__main__":
    asyncio.run(main())
