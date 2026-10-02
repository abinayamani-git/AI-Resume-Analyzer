"""
Job description vs resume matching logic.
"""

from app.models import JobMatchResult
from app.services.analyzer import detect_skills


def analyze_job_match(resume_text: str, job_description: str, resume_skills: list[str] | None = None) -> JobMatchResult:
    """
    Compare resume skills/keywords with a job description.

    Returns an *estimated* job match percentage — not a hiring guarantee.
    """
    jd = (job_description or "").strip()
    if not jd:
        return JobMatchResult(
            job_match_percentage=None,
            explanation="No job description was provided. General resume analysis was performed instead.",
        )

    if len(jd) < 30:
        return JobMatchResult(
            job_match_percentage=None,
            explanation="Job description is too short to compare meaningfully. Paste a fuller description and try again.",
        )

    resume_skills = resume_skills or detect_skills(resume_text)
    jd_skills = detect_skills(jd)

    matched = [s for s in jd_skills if s in resume_skills]
    missing = [s for s in jd_skills if s not in resume_skills]

    # Expand important keywords beyond catalog hits (simple frequency nouns)
    important = jd_skills[:12]

    if jd_skills:
        percentage = int(round((len(matched) / len(jd_skills)) * 100))
    else:
        # JD had no catalog skills — soft score based on shared tokens
        resume_tokens = set(resume_text.lower().split())
        jd_tokens = {t.strip(".,()[]") for t in jd.lower().split() if len(t) > 4}
        overlap = resume_tokens & jd_tokens
        percentage = min(85, int(len(overlap) / max(len(jd_tokens), 1) * 100))
        important = sorted(list(overlap))[:12]

    # Alignment blurbs
    exp_align = (
        "Your experience keywords overlap well with the role requirements."
        if percentage >= 70
        else "Experience alignment is moderate — emphasize role-relevant responsibilities and tools."
        if percentage >= 40
        else "Experience alignment appears low — tailor bullets toward the job's core responsibilities."
    )
    proj_align = (
        "Projects appear relevant to several technologies mentioned in the job description."
        if matched
        else "Consider adding projects that demonstrate the missing skills listed below."
    )

    recommended = missing[:8] or ["Review the job description for domain-specific tools to learn next."]

    explanation = (
        f"Estimated job match is {percentage}% based on overlap between skills detected in your resume "
        f"and requirements inferred from the job description. This is an advisory signal, not a prediction "
        f"of interview or hiring outcomes."
    )

    return JobMatchResult(
        job_match_percentage=percentage,
        matched_skills=matched,
        missing_skills=missing,
        important_keywords=important,
        recommended_skills=recommended if isinstance(recommended, list) else [recommended],
        experience_alignment=exp_align,
        project_alignment=proj_align,
        explanation=explanation,
    )
