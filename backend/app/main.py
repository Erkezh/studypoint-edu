from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router_v1
from app.core.config import settings
from app.core.errors import install_exception_handlers
from app.core.logging import configure_logging
from app.db.session import close_engine, init_engine
from app.services.health_service import get_readiness_checks
from app.utils.redis import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(environment=settings.environment)
    init_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout_sec=settings.db_pool_timeout_sec,
        pool_recycle_sec=settings.db_pool_recycle_sec,
        connect_timeout_sec=settings.db_connect_timeout_sec,
        command_timeout_sec=settings.db_command_timeout_sec,
    )
    try:
        await init_redis(settings.redis_url)
        await get_readiness_checks()
        yield
    finally:
        await close_redis()
        await close_engine()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В разработке разрешаем все источники. В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP методы (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

from fastapi import Request

@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    # Process the request
    response = await call_next(request)
    
    # Disable caching for all API endpoints to ensure real-time updates
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
    return response

install_exception_handlers(app)
app.include_router(api_router_v1, prefix=settings.api_v1_prefix)

# Статическая раздача файлов плагинов
# Плагины доступны по пути /static/plugins/{plugin_id}/{version}/{file}
plugins_dir = Path(settings.plugins_dir)
plugins_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/plugins", StaticFiles(directory=str(plugins_dir)), name="plugins")


# ============= TEMPORARY DEBUG ENDPOINT — DELETE AFTER TESTING =============
from fastapi.responses import HTMLResponse

@app.get("/debug/test-student-login", response_class=HTMLResponse)
async def debug_test_student_login():
    """Temporary endpoint: creates a student, then tries to log in. Open in browser."""
    import random
    from sqlalchemy import select, text
    from app.db.session import get_sessionmaker
    from app.models.user import User
    from app.models.enums import UserRole
    from app.models.profile import StudentProfile
    from app.core.security import hash_password, verify_password

    log_lines = []
    log = lambda msg: log_lines.append(msg)

    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        async with session.begin():
            # Step 1: Count existing students
            result = await session.execute(
                select(User).where(User.role == UserRole.STUDENT)
            )
            students = result.scalars().all()
            log(f"📊 Total students in DB: {len(students)}")
            for s in students[:10]:
                log(f"  - username={s.email}, active={s.is_active}, has_teacher={s.teacher_id is not None}, hash_start={s.password_hash[:25] if s.password_hash else 'NONE'}")

            # Step 2: Create a fresh test student
            test_username = f"debuguser{random.randint(1000, 9999)}"
            test_password = "TestPass1!"
            test_hash = hash_password(test_password)
            log(f"\n🔧 Creating test student: {test_username} / {test_password}")
            log(f"   Hash: {test_hash[:40]}...")

            new_student = User(
                email=test_username,
                password_hash=test_hash,
                full_name="Debug Test Student",
                role=UserRole.STUDENT,
                is_active=True,
            )
            session.add(new_student)
            session.add(StudentProfile(user_id=new_student.id, grade_level=5, plain_password=test_password))
            await session.flush()
            new_id = str(new_student.id)
            log(f"   Created with ID: {new_id}")

    # Step 3: Try to look up and verify password (in a new session, simulating login)
    async with sessionmaker() as session:
        async with session.begin():
            log(f"\n🔑 Simulating login for: {test_username}")
            result = await session.execute(
                select(User).where(User.email == test_username)
            )
            found_user = result.scalar_one_or_none()

            if found_user is None:
                log("❌ FAIL: User NOT FOUND in database after creation!")
            else:
                log(f"✅ User found: email={found_user.email}, active={found_user.is_active}, role={found_user.role}")
                log(f"   Hash from DB: {found_user.password_hash[:40]}...")

                # Verify password
                pw_ok = verify_password(test_password, found_user.password_hash)
                if pw_ok:
                    log("✅ PASSWORD VERIFIED SUCCESSFULLY!")
                else:
                    log("❌ FAIL: Password verification FAILED!")

                    # Extra debug: re-hash and compare
                    re_hash = hash_password(test_password)
                    log(f"   Re-hash of same password: {re_hash[:40]}...")
                    log(f"   verify(password, re_hash) = {verify_password(test_password, re_hash)}")

            # Step 4: Test with existing teacher-created students
            log("\n\n📋 Testing ALL existing students' password verification:")
            all_students_result = await session.execute(
                select(User, StudentProfile).outerjoin(StudentProfile, User.id == StudentProfile.user_id).where(User.role == UserRole.STUDENT)
            )
            rows = all_students_result.all()
            for row in rows:
                user_obj = row[0]
                profile = row[1]
                plain_pw = profile.plain_password if profile else None
                if plain_pw:
                    pw_check = verify_password(plain_pw, user_obj.password_hash)
                    log(f"  Student {user_obj.email}: plain_pw={plain_pw}, verify={pw_check}")
                else:
                    log(f"  Student {user_obj.email}: NO plain_password stored in profile")

    html = "<html><body style='font-family: monospace; white-space: pre; padding: 20px; background: #1a1a2e; color: #e0e0e0;'>"
    html += "\n".join(log_lines)
    html += "\n\n--- END OF DEBUG ---"
    html += "</body></html>"
    return HTMLResponse(content=html)
# ============= END TEMPORARY DEBUG ENDPOINT =============

