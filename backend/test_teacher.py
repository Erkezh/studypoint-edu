import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.db.session import init_engine, get_db_session
from app.services.teacher_service import TeacherService
from app.schemas.teacher import TeacherCreateStudentRequest
from sqlalchemy import select
from app.models.user import User

async def run_test():
    init_engine(settings.database_url)
    async for session in get_db_session():
        # Find a teacher
        stmt = select(User).where(User.role == "TEACHER").limit(1)
        teacher = (await session.execute(stmt)).scalar_one_or_none()
        if not teacher:
            print("No teacher found, cannot test properly. Let's make one first.")
            # For test: temporarily create a teacher
            from app.models.enums import UserRole
            import uuid
            teacher = User(id=uuid.uuid4(), email="teacher_test@example.com", full_name="Test Teacher", password_hash="hash", role=UserRole.TEACHER)
            session.add(teacher)
            await session.commit()
            await session.refresh(teacher)
            
        svc = TeacherService(session)
        req = TeacherCreateStudentRequest(first_name="Маңғыстау", last_name="Әл-Фараби", grade_id=5)
        res = await svc.create_student(str(teacher.id), req)
        
        print("Generated student response:", res)
        # Not committing so we don't pollute the dev db permanently
        # await session.commit()

if __name__ == "__main__":
    asyncio.run(run_test())
