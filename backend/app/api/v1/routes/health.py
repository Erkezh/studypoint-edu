from __future__ import annotations

from fastapi import APIRouter

from app.core.errors import AppError
from app.schemas.base import ApiResponse
from app.services.health_service import DependencyNotReadyError, get_readiness_checks

router = APIRouter()


@router.get("/health/live", response_model=ApiResponse[dict[str, str]])
async def live() -> ApiResponse[dict[str, str]]:
    return ApiResponse(data={"status": "live"})


@router.get("/health/ready", response_model=ApiResponse[dict[str, object]])
async def ready() -> ApiResponse[dict[str, object]]:
    try:
        checks = await get_readiness_checks()
    except DependencyNotReadyError as exc:
        raise AppError(
            status_code=503,
            code="service_unavailable",
            message=str(exc),
            details={"service": exc.service},
        ) from exc

    return ApiResponse(
        data={
            "status": "ready",
            "checks": checks,
        }
    )
