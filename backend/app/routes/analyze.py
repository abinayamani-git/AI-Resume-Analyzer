"""Resume analysis and job-match endpoints."""

from fastapi import APIRouter, HTTPException

from app.models import AnalysisResponse, AnalyzeRequest, JobMatchRequest, JobMatchResult
from app.services import ai_service
from app.services.resume_parser import extract_resume_text
from app.services.storage import save_analysis
from app.utils.file_utils import original_filename_from_path, resolve_upload_path

router = APIRouter(tags=["analyze"])


@router.post("/api/analyze", response_model=AnalysisResponse)
def analyze_resume(payload: AnalyzeRequest):
    """
    Extract resume text and run the modular AI analysis service.
    Works without an API key via the rule-based fallback analyzer.
    """
    path = resolve_upload_path(payload.file_id)
    filename = original_filename_from_path(path)

    try:
        text = extract_resume_text(path)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Resume extraction failed. Please try a different PDF or DOCX file.",
        )

    job_description = (payload.job_description or "").strip() or None
    if job_description is not None and len(job_description) < 20:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Paste a fuller description or leave it empty.",
        )

    try:
        result = ai_service.analyze_resume(text, job_description)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Analysis failed unexpectedly. Please try again.",
        )

    analysis_id = save_analysis(payload.file_id, filename, result)

    return AnalysisResponse(
        analysis_id=analysis_id,
        filename=filename,
        analysis_mode=result.get("analysis_mode", "fallback"),
        personal_info=result["personal_info"],
        detected_sections=result.get("detected_sections", []),
        detected_skills=result.get("detected_skills", []),
        strong_skills=result.get("strong_skills", []),
        missing_skills=result.get("missing_skills", []),
        recommended_skills=result.get("recommended_skills", []),
        ats_score=result.get("ats_score", 0),
        ats_breakdown=result["ats_breakdown"],
        section_scores=result["section_scores"],
        job_match=result.get("job_match") or JobMatchResult(),
        recommendations=result.get("recommendations", []),
        summary_analysis=result["summary_analysis"],
        projects=result.get("projects", []),
        experience=result.get("experience", []),
        education=result.get("education", []),
        certifications=result.get("certifications", []),
        achievements=result.get("achievements", []),
        message="Analysis complete",
    )


@router.post("/api/job-match", response_model=JobMatchResult)
def job_match(payload: JobMatchRequest):
    """Standalone job-match comparison for an already uploaded resume."""
    if not payload.job_description or len(payload.job_description.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid job description (at least 20 characters).",
        )

    path = resolve_upload_path(payload.file_id)
    text = extract_resume_text(path)
    return ai_service.analyze_job_match(text, payload.job_description)
