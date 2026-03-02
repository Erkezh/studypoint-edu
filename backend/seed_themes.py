import asyncio
from app.db.session import init_engine, get_sessionmaker
from app.core.config import settings
from app.models.topic import Topic
from app.models.catalog import Skill, Grade
from sqlalchemy import select

async def main():
    init_engine(str(settings.database_url))
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        # 1. Create Theme
        theme = Topic(slug='math-basics', title='Math Basics', icon='📐', order=10, is_published=True)
        session.add(theme)
        await session.flush()
        
        # 2. Create Subtheme
        subtheme = Topic(slug='addition', title='Addition', parent_id=theme.id, order=20, is_published=True)
        session.add(subtheme)
        await session.flush()
        
        # 3. Find Grade 1
        grade_res = await session.execute(select(Grade).where(Grade.number == 1))
        grade = grade_res.scalar_one_or_none()
        if not grade:
            grade = Grade(number=1, label="Г1", title="1 сынып", description="")
            session.add(grade)
            await session.flush()

        # 4. Create Skill in Subtheme
        skill1 = Skill(
            subject_id=1,
            grade_id=grade.id,
            topic_id=subtheme.id,
            code="A.1",
            title="Single-digit addition limits to 10",
            difficulty=1,
            tags=["math", "addition"],
            is_published=True,
            description="Add numbers up to 10"
        )
        session.add(skill1)
        
        # 5. Create Standalone Skill in Theme
        skill2 = Skill(
            subject_id=1,
            grade_id=grade.id,
            topic_id=theme.id,
            code="A.0",
            title="Introduction to numbers",
            difficulty=1,
            tags=["math"],
            is_published=True,
            description="Count to 10"
        )
        session.add(skill2)
        
        await session.commit()
        print("Seeded successfully!")

if __name__ == "__main__":
    asyncio.run(main())
