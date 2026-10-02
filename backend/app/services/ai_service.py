"""
Modular AI analysis service.

Architecture:
  - analyze_resume(text)
  - analyze_job_match(resume_text, job_description)
  - generate_recommendations(analysis)

Today: rule-based fallback (works with no API key).
Later: swap AI_PROVIDER=openai and implement _llm_* helpers without rewriting routes.
"""

from typing import Any, Optional

from app.config import settings
from app.models import JobMatchResult
from app.services.analyzer import generate_recommendations as rule_recommendations
from app.services.analyzer import run_rule_based_analysis
from app.services.job_matcher import analyze_job_match as rule_job_match


def _use_llm() -> bool:
    """True only when an API key is configured and provider is set to openai."""
    return (
        settings.ai_provider.lower() == "openai"
        and bool(settings.openai_api_key)
        and settings.openai_api_key.strip() not in ("", "your-key-here")
    )


def analyze_resume(text: str, job_description: Optional[str] = None) -> dict[str, Any]:
    """
    Analyze resume text.

    Returns a dict of analysis fields plus:
      - analysis_mode: "fallback" | "llm"
      - job_match: JobMatchResult
    """
    if _use_llm():
        # Placeholder for future LLM integration — falls back safely if not implemented
        try:
            return _llm_analyze_resume(text, job_description)
        except Exception:
            # Never break the app if the LLM call fails
            result = run_rule_based_analysis(text, job_description)
            result["analysis_mode"] = "fallback"
            result["job_match"] = analyze_job_match(text, job_description or "", result.get("_resume_skills"))
            return result

    result = run_rule_based_analysis(text, job_description)
    result["analysis_mode"] = "fallback"
    result["job_match"] = analyze_job_match(text, job_description or "", result.get("_resume_skills"))
    return result


def analyze_job_match(resume_text: str, job_description: str, resume_skills: list[str] | None = None) -> JobMatchResult:
    """Independent job-match entry point (used by /api/job-match)."""
    if _use_llm():
        try:
            return _llm_analyze_job_match(resume_text, job_description)
        except Exception:
            return rule_job_match(resume_text, job_description, resume_skills)
    return rule_job_match(resume_text, job_description, resume_skills)


def generate_recommendations(analysis: dict[str, Any]) -> list[str]:
    """Independent recommendations entry point for future LLM rewriting."""
    if _use_llm():
        try:
            return _llm_generate_recommendations(analysis)
        except Exception:
            pass

    # Rebuild from analysis dict if present
    if analysis.get("recommendations"):
        return analysis["recommendations"]

    return rule_recommendations(
        analysis.get("detected_sections", []),
        analysis.get("detected_skills", []),
        analysis.get("missing_skills", []),
        analysis.get("experience", []),
        analysis.get("projects", []),
        analysis.get("summary_analysis"),
        analysis.get("personal_info"),
        has_job=bool(analysis.get("job_match") and analysis["job_match"].job_match_percentage is not None),
    )


# ---------------------------------------------------------------------------
# Future LLM hooks — implement without changing route handlers
# ---------------------------------------------------------------------------

def _llm_analyze_resume(text: str, job_description: Optional[str]) -> dict[str, Any]:
    """
    Future: call OpenAI (or another provider) with a structured JSON schema prompt.
    For now, raise to trigger safe fallback.
    """
    raise NotImplementedError("LLM resume analysis is not configured yet. Using rule-based fallback.")


def _llm_analyze_job_match(resume_text: str, job_description: str) -> JobMatchResult:
    raise NotImplementedError("LLM job match is not configured yet.")


def _llm_generate_recommendations(analysis: dict[str, Any]) -> list[str]:
    raise NotImplementedError("LLM recommendations are not configured yet.")
