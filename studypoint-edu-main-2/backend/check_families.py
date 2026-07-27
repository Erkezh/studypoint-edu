import asyncio
from sqlalchemy import select
from app.db.session import _engine, create_async_engine, async_sessionmaker
from app.models.user import User

async def main():
    engine = create_async_engine("postgresql+asyncpg://erkenazzhanabay@localhost:5432/ixl")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        stmt = select(User).where(User.role == 'PARENT')
        res = await session.execute(stmt)
        parents = res.scalars().unique().all()
        for p in parents:
            stmt2 = select(User).where(User.parent_id == p.id)
            res2 = await session.execute(stmt2)
            children = res2.scalars().unique().all()
            print(f"Parent {p.email} has {len(children)} children.")

if __name__ == "__main__":
    asyncio.run(main())
