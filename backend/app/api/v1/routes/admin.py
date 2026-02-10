from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.rbac import require_roles
from app.schemas.admin import BulkImportRequest
from app.schemas.base import ApiResponse
from app.services.admin_service import AdminService

from app.api.v1.routes.admin_routes import grades, questions, skills, subjects, topics
from app.plugins.router import router as plugins_router

router = APIRouter()
router.include_router(subjects.router, prefix="/subjects", tags=["Admin"])
router.include_router(grades.router, prefix="/grades", tags=["Admin"])
router.include_router(topics.router, prefix="/topics", tags=["Admin"])
router.include_router(skills.router, prefix="/skills", tags=["Admin"])
router.include_router(questions.router, prefix="/questions", tags=["Admin"])
router.include_router(plugins_router, prefix="/plugins", tags=["Admin"])


@router.post("/bulk_import", response_model=ApiResponse[dict], dependencies=[Depends(require_roles("ADMIN"))], tags=["Admin"])
async def bulk_import(body: BulkImportRequest, svc: AdminService = Depends()):
    res = await svc.bulk_import(body)
    return ApiResponse(data=res.model_dump(mode="json"))
