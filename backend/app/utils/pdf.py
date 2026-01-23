from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _pagesize(paper: str | None):
    if paper and paper.lower() == "a4":
        return A4
    return LETTER


def build_practice_session_report_pdf(
    *,
    paper: str | None,
    header: dict[str, Any],
    rows: list[dict[str, Any]],
) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=_pagesize(paper), leftMargin=0.6 * inch, rightMargin=0.6 * inch)
    styles = getSampleStyleSheet()

    story: list[Any] = []
    story.append(Paragraph("Practice Session Report", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))

    meta_table = Table(
        [
            ["Student", header.get("student")],
            ["Skill", header.get("skill")],
            ["Date", header.get("date")],
            ["Current SmartScore", str(header.get("current_smartscore", 0))],
            ["Best SmartScore", str(header.get("best_smartscore", 0))],
            ["Questions Answered", str(header.get("questions_answered", 0))],
            ["Correct / Incorrect", f"{header.get('correct', 0)} / {header.get('incorrect', 0)}"],
            ["Active Time (sec)", str(header.get("active_time_seconds", 0))],
        ],
        hAlign="LEFT",
        colWidths=[2.2 * inch, 4.8 * inch],
    )
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("Questions Log", styles["Heading2"]))
    story.append(Spacer(1, 0.1 * inch))

    table_data = [
        [
            "#",
            "Timestamp",
            "Question",
            "Student Answer",
            "Correct Answer",
            "Correct?",
            "Time (s)",
            "SmartScore",
        ]
    ]
    for i, r in enumerate(rows, start=1):
        table_data.append(
            [
                str(i),
                r.get("answered_at", ""),
                (r.get("question") or "")[:120],
                (r.get("submitted_answer") or "")[:60],
                (r.get("correct_answer") or "")[:60],
                "✓" if r.get("is_correct") else "✗",
                str(r.get("time_spent_sec", 0)),
                f"{r.get('smartscore_before', 0)}→{r.get('smartscore_after', 0)}",
            ]
        )

    log_table = Table(table_data, repeatRows=1, hAlign="LEFT", colWidths=[0.35 * inch, 1.2 * inch, 2.6 * inch, 1.1 * inch, 1.1 * inch, 0.55 * inch, 0.55 * inch, 0.8 * inch])
    log_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(log_table)

    doc.build(story)
    return buf.getvalue()


def build_assignment_report_pdf(*, paper: str | None, header: dict[str, Any], rows: list[dict[str, Any]]) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=_pagesize(paper), leftMargin=0.6 * inch, rightMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    story: list[Any] = []
    story.append(Paragraph("Assignment Report (Score Grid)", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))

    meta_table = Table(
        [
            ["Assignment", header.get("assignment_id")],
            ["Skill", header.get("skill")],
            ["Target SmartScore", str(header.get("target_smartscore", 80))],
            ["Due Date", header.get("due_at")],
            ["Summary", header.get("summary")],
        ],
        hAlign="LEFT",
        colWidths=[2.2 * inch, 4.8 * inch],
    )
    meta_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey), ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold")]))
    story.append(meta_table)
    story.append(Spacer(1, 0.25 * inch))

    table_data = [["Student", "Status", "Best", "Last", "Questions", "Time (s)", "Last Activity"]]
    for r in rows:
        table_data.append(
            [
                r.get("student"),
                r.get("status"),
                str(r.get("best_smartscore", 0)),
                str(r.get("last_smartscore", 0)),
                str(r.get("questions_answered", 0)),
                str(r.get("time_spent_seconds", 0)),
                r.get("last_activity_at") or "",
            ]
        )
    grid = Table(table_data, repeatRows=1, hAlign="LEFT", colWidths=[2.2 * inch, 1.0 * inch, 0.55 * inch, 0.55 * inch, 0.75 * inch, 0.65 * inch, 1.5 * inch])
    grid.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(grid)
    doc.build(story)
    return buf.getvalue()


def build_certificate_pdf(
    *,
    paper: str | None,
    title: str,
    student_name: str,
    skill_name: str,
    date_str: str,
    awarded_by: str | None,
) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=_pagesize(paper), leftMargin=0.9 * inch, rightMargin=0.9 * inch, topMargin=1.0 * inch, bottomMargin=1.0 * inch)
    styles = getSampleStyleSheet()
    story: list[Any] = []
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("This certificate is awarded to", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"<b>{student_name}</b>", styles["Title"]))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(f"For achievement in: <b>{skill_name}</b>", styles["BodyText"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(f"Date: {date_str}", styles["BodyText"]))
    if awarded_by:
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph(f"Awarded by: {awarded_by}", styles["BodyText"]))
    doc.build(story)
    return buf.getvalue()

