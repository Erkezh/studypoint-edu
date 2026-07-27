from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from app.core.deps import get_current_user
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/practice-sessions/{session_id}.pdf")
async def practice_session_pdf(
    session_id: str,
    paper: str | None = None,
    user=Depends(get_current_user),
    svc: ReportService = Depends(),
):
    role_value = getattr(user.role, "value", user.role)
    pdf_bytes = await svc.practice_session_pdf(
        requester_id=user.id,
        requester_role=role_value,
        session_id=session_id,
        paper=paper,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="practice-session-{session_id}.pdf"'},
    )


@router.get("/assignments/{assignment_id}.pdf")
async def assignment_pdf(
    assignment_id: str,
    paper: str | None = None,
    user=Depends(get_current_user),
    svc: ReportService = Depends(),
):
    role_value = getattr(user.role, "value", user.role)
    pdf_bytes = await svc.assignment_pdf(
        requester_id=user.id,
        requester_role=role_value,
        assignment_id=assignment_id,
        paper=paper,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="assignment-{assignment_id}.pdf"'},
    )
