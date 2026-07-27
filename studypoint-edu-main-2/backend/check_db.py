import asyncio
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User

async def main():
    async with async_session_maker() as session:
        # get all parents
        stmt = select(User).where(User.role == 'PARENT')
        res = await session.execute(stmt)
        parents = res.scalars().unique().all()
        for p in parents:
            print(f"Parent: {p.email}, {p.role}")
            
            stmt2 = select(User).where(User.parent_id == p.id)
            res2 = await session.execute(stmt2)
            children = res2.scalars().unique().all()
            print(f"  Children: {[c.email for c in children]}")

if __name__ == "__main__":
    asyncio.run(main())
