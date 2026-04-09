import asyncio
from app.db.session import async_session_maker
from app.models.user import User
from sqlalchemy import select

async def main():
    async with async_session_maker() as session:
        stmt = select(User).where(User.role == "TEACHER")
        teachers = (await session.execute(stmt)).scalars().all()
        print(f"Found {len(teachers)} teachers")
        for t in teachers:
            print(f"Teacher: {t.full_name} ({t.email})")
            stmt2 = select(User).where(User.teacher_id == t.id)
            students = (await session.execute(stmt2)).scalars().all()
            print(f"  Students (teacher_id): {[s.full_name for s in students]}")
            
            stmt3 = select(User).where(User.parent_id == t.id)
            children = (await session.execute(stmt3)).scalars().all()
            print(f"  Children (parent_id): {[c.full_name for c in children]}")

if __name__ == "__main__":
    asyncio.run(main())
