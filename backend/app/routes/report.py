"""PDF report download endpoint."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.models import ReportMeta
from app.services.report_service import build_report_pdf
from app.services.storage import get_analysis

router = APIRouter(tags=["report"])


@router.get("/api/report/{analysis_id}")
def download_report(analysis_id: str):
    """Generate and download a simple PDF report for a stored analysis."""
    analysis = get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found. Please run analysis again.")

    try:
        pdf_bytes = build_report_pdf(analysis)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not generate the PDF report.")

    filename = f"resume-analysis-{analysis_id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/api/report/{analysis_id}/meta", response_model=ReportMeta)
def report_meta(analysis_id: str):
    analysis = get_analysis(analysis_id)
    return ReportMeta(
        analysis_id=analysis_id,
        available=analysis is not None,
        message="Report available" if analysis else "Analysis not found",
    )
