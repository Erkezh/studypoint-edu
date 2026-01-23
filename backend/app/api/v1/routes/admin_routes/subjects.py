from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.rbac import require_roles
from app.schemas.admin import SubjectCreate, SubjectUpdate
from app.schemas.base import ApiResponse
from app.schemas.catalog import SubjectResponse
from app.services.admin_service import AdminService

router = APIRouter(dependencies=[Depends(require_roles("ADMIN"))])


@router.get("", response_model=ApiResponse[list[SubjectResponse]])
async def list_subjects(svc: AdminService = Depends()):
    rows = await svc.list_subjects()
    return ApiResponse(data=[SubjectResponse(id=s.id, slug=s.slug, title=s.title) for s in rows])


@router.post("", response_model=ApiResponse[SubjectResponse])
async def create_subject(body: SubjectCreate, svc: AdminService = Depends()):
    s = await svc.create_subject(body)
    return ApiResponse(data=SubjectResponse(id=s.id, slug=s.slug, title=s.title))


@router.patch("/{subject_id}", response_model=ApiResponse[SubjectResponse])
async def update_subject(subject_id: int, body: SubjectUpdate, svc: AdminService = Depends()):
    s = await svc.update_subject(subject_id, body)
    return ApiResponse(data=SubjectResponse(id=s.id, slug=s.slug, title=s.title))


@router.delete("/{subject_id}", response_model=ApiResponse[dict])
async def delete_subject(subject_id: int, svc: AdminService = Depends()):
    await svc.delete_subject(subject_id)
    return ApiResponse(data={"ok": True})

