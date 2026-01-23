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
    return ApiResponse(data=[GradeResponse(id=g.id, number=g.number, title=g.title) for g in rows])


@router.post("", response_model=ApiResponse[GradeResponse])
async def create_grade(body: GradeCreate, svc: AdminService = Depends()):
    g = await svc.create_grade(body)
    return ApiResponse(data=GradeResponse(id=g.id, number=g.number, title=g.title))


@router.patch("/{grade_id}", response_model=ApiResponse[GradeResponse])
async def update_grade(grade_id: int, body: GradeUpdate, svc: AdminService = Depends()):
    g = await svc.update_grade(grade_id, body)
    return ApiResponse(data=GradeResponse(id=g.id, number=g.number, title=g.title))


@router.delete("/{grade_id}", response_model=ApiResponse[dict])
async def delete_grade(grade_id: int, svc: AdminService = Depends()):
    await svc.delete_grade(grade_id)
    return ApiResponse(data={"ok": True})

