from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.rbac import require_roles
from app.schemas.admin import GradeCreate, GradeUpdate
from app.schemas.base import ApiResponse
from app.schemas.catalog import GradeResponse
from app.services.admin_service import AdminService

router = APIRouter(dependencies=[Depends(require_roles("ADMIN"))])


@router.get("", response_model=ApiResponse[list[GradeResponse]])
async def list_grades(svc: AdminService = Depends()):
    rows = await svc.list_grades()
    return ApiResponse(data=[GradeResponse(id=g.id, number=g.number, label=g.label, title=g.title, description=g.description) for g in rows])


@router.post("", response_model=ApiResponse[GradeResponse])
async def create_grade(body: GradeCreate, svc: AdminService = Depends()):
    g = await svc.create_grade(body)
    return ApiResponse(data=GradeResponse(id=g.id, number=g.number, label=g.label, title=g.title, description=g.description))


@router.patch("/{grade_id}", response_model=ApiResponse[GradeResponse])
async def update_grade(grade_id: int, body: GradeUpdate, svc: AdminService = Depends()):
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("UPDATE GRADE id=%s body=%s body_dump=%s", grade_id, body, body.model_dump(exclude_unset=True))
    g = await svc.update_grade(grade_id, body)
    logger.warning("UPDATE GRADE RESULT id=%s label=%s title=%s", g.id, g.label, g.title)
    return ApiResponse(data=GradeResponse(id=g.id, number=g.number, label=g.label, title=g.title, description=g.description))


@router.delete("/{grade_id}", response_model=ApiResponse[dict])
async def delete_grade(grade_id: int, svc: AdminService = Depends()):
    await svc.delete_grade(grade_id)
    return ApiResponse(data={"ok": True})

