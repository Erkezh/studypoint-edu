import asyncio
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.db.session import init_engine, get_db_session
from app.services.admin_service import AdminService
from app.schemas.admin import AdminUserResponse

async def test_users():
    load_dotenv()
    init_engine(settings.database_url)
    async for session in get_db_session():
        svc = AdminService(session)
        users = await svc.get_users()
        print(f"Total users found: {len(users)}")
        for u in users[:2]:
            try:
                # Same map performed by the endpoint
                res = AdminUserResponse(
                    id=str(u.id),
                    email=u.email,
                    full_name=u.full_name,
                    role=u.role,
                    is_active=u.is_active,
                )
                print(f"Mapped successfully: {res}")
            except Exception as e:
                print(f"Mapping error for user {u.id}: {e}")

if __name__ == "__main__":
    asyncio.run(test_users())
