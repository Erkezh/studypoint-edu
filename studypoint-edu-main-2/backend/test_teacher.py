import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.role == "TEACHER")
        teachers = (await session.execute(stmt)).scalars().all()
        print(f"Found {len(teachers)} teachers")
        for t in teachers:
            print(f"Teacher: {t.full_name} ({t.id})")
            stmt2 = select(User).where(User.teacher_id == t.id)
            students = (await session.execute(stmt2)).scalars().all()
            print(f"  Students: {[s.full_name for s in students]}")

if __name__ == "__main__":
    asyncio.run(main())
