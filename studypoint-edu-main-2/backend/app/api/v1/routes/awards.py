from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from app.core.deps import get_current_user
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/certificates/{type}.pdf")
async def certificate_pdf(
    type: str,
    skill_id: int,
    student_id: str | None = None,
    date: str | None = None,
    awarded_by: str | None = None,
    related_session_id: str | None = None,
    paper: str | None = None,
    user=Depends(get_current_user),
    svc: ReportService = Depends(),
):
    role_value = getattr(user.role, "value", user.role)
    pdf_bytes = await svc.certificate_pdf(
        requester_id=user.id,
        requester_role=role_value,
        student_id=student_id,
        skill_id=skill_id,
        type=type.upper(),
        paper=paper,
        date_str=date,
        awarded_by=awarded_by,
        related_session_id=related_session_id,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="certificate-{type.lower()}-{skill_id}.pdf"'},
    )

