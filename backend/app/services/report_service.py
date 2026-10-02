"""
Generate a simple PDF report from a stored analysis.
"""

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_report_pdf(analysis: dict[str, Any]) -> bytes:
    """Return PDF bytes for the given analysis dictionary."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=0.75 * inch, rightMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Heading1"],
        textColor=colors.HexColor("#1D4ED8"),
        spaceAfter=12,
    )
    heading = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#0F172A"),
        fontSize=13,
        spaceBefore=14,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        textColor=colors.HexColor("#0F172A"),
        fontSize=10,
        leading=14,
    )
    muted = ParagraphStyle(
        "Muted",
        parent=body,
        textColor=colors.HexColor("#64748B"),
        fontSize=9,
    )

    story = []
    story.append(Paragraph("AI Resume Analyzer — Analysis Report", title_style))
    story.append(Paragraph(
        "Estimated insights for portfolio and career improvement. Not a real ATS vendor score.",
        muted,
    ))
    story.append(Spacer(1, 8))

    filename = analysis.get("filename", "resume")
    ats = analysis.get("ats_score", "—")
    job_match = analysis.get("job_match") or {}
    if isinstance(job_match, dict):
        jm = job_match.get("job_match_percentage")
    else:
        jm = getattr(job_match, "job_match_percentage", None)

    summary_rows = [
        ["Resume", str(filename)],
        ["Estimated ATS Compatibility Score", f"{ats}/100"],
        ["Estimated Job Match", f"{jm}%" if jm is not None else "N/A (no job description)"],
        ["Analysis Mode", str(analysis.get("analysis_mode", "fallback"))],
    ]
    table = Table(summary_rows, colWidths=[2.6 * inch, 4 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)

    def bullet_section(title: str, items: list):
        story.append(Paragraph(title, heading))
        if not items:
            story.append(Paragraph("None detected.", body))
            return
        for item in items:
            story.append(Paragraph(f"• {item}", body))

    bullet_section("Detected Skills", analysis.get("detected_skills") or [])
    bullet_section("Missing / Recommended Skills", analysis.get("missing_skills") or analysis.get("recommended_skills") or [])
    bullet_section("AI-Assisted Recommendations", analysis.get("recommendations") or [])

    section_scores = analysis.get("section_scores") or {}
    if hasattr(section_scores, "model_dump"):
        section_scores = section_scores.model_dump()
    if section_scores:
        story.append(Paragraph("Section Scores", heading))
        rows = [["Section", "Score"]] + [[k.replace("_", " ").title(), f"{v}%"] for k, v in section_scores.items()]
        st = Table(rows, colWidths=[3 * inch, 1.5 * inch])
        st.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(st)

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Disclaimer: Scores are estimated using rule-based analysis for learning and portfolio purposes.",
        muted,
    ))

    doc.build(story)
    return buffer.getvalue()
