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
    init_engine(settings.database_url)
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
