"""
Rule-based resume analysis engine.

This is the fallback analyzer that works without any external AI API.
It uses pattern matching, section detection, and a modular skill catalog.
"""

import re
from typing import Optional

from app.models import (
    ATSBreakdown,
    EducationItem,
    ExperienceItem,
    PersonalInfo,
    ProjectItem,
    SectionScores,
    SummaryAnalysis,
)
from app.services.skills_catalog import (
    ROLE_RECOMMENDATIONS,
    SKILL_CATALOG,
    SKILL_LOOKUP,
)
from app.utils.text_utils import (
    extract_email,
    extract_phone,
    extract_url,
    find_section_block,
    has_action_verb,
    has_quantifiable,
    normalize_for_match,
    split_lines,
)


def detect_skills(text: str) -> list[str]:
    """Detect skills from the modular catalog using word-boundary aware matching."""
    lower = normalize_for_match(text)
    found: dict[str, int] = {}

    for skill in SKILL_CATALOG:
        terms = [skill.name] + skill.aliases
        for term in terms:
            # Word-boundary-ish match; allow punctuation around term
            pattern = rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])"
            if re.search(pattern, lower):
                found[skill.name] = max(found.get(skill.name, 0), skill.priority)
                break

    # Sort by priority then name for stable output
    return sorted(found.keys(), key=lambda n: (-found[n], n))


def extract_personal_info(text: str) -> PersonalInfo:
    """Heuristic extraction of contact details from the resume header area."""
    header = "\n".join(text.split("\n")[:25])
    email = extract_email(text)
    phone = extract_phone(text)
    linkedin = extract_url(text, "linkedin.com")
    github = extract_url(text, "github.com")

    # Name heuristic: first non-empty line that is not an email/url/phone
    name = None
    for line in text.split("\n")[:10]:
        candidate = line.strip()
        if not candidate or len(candidate) > 60:
            continue
        if "@" in candidate or "http" in candidate.lower():
            continue
        if re.search(r"\d{5,}", candidate):
            continue
        if re.match(r"^[A-Za-z][A-Za-z\s.'\-]+$", candidate):
            name = candidate
            break

    location = None
    loc_match = re.search(
        r"(?i)\b([A-Za-z\s]+,\s*[A-Za-z\s]+(?:,\s*[A-Za-z\s]+)?)\b",
        header,
    )
    if loc_match:
        location = loc_match.group(1).strip()

    return PersonalInfo(
        name=name,
        email=email,
        phone=phone,
        linkedin=linkedin,
        github=github,
        location=location,
    )


def detect_sections(text: str) -> list[str]:
    """Return which standard resume sections appear in the document."""
    lower = normalize_for_match(text)
    mapping = {
        "Summary": ["summary", "objective", "professional summary", "profile"],
        "Education": ["education", "academic background"],
        "Experience": ["experience", "work experience", "employment", "professional experience"],
        "Projects": ["projects", "personal projects", "academic projects"],
        "Skills": ["skills", "technical skills", "technologies", "tech stack"],
        "Certifications": ["certifications", "certificates", "licenses"],
        "Achievements": ["achievements", "accomplishments", "awards"],
    }
    present = []
    for section, keywords in mapping.items():
        if any(k in lower for k in keywords):
            present.append(section)
    return present


def analyze_summary(text: str, skills: list[str], name: Optional[str]) -> SummaryAnalysis:
    """Inspect the professional summary and propose an improved version."""
    block = find_section_block(text, ["summary", "objective", "professional summary", "profile", "about me"])
    lines = split_lines(block)
    # Drop the heading line itself
    body_lines = lines[1:] if lines else []
    current = " ".join(body_lines).strip()
    if not current:
        # Fallback: use first substantial paragraph
        paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 80]
        current = paras[0][:400] if paras else ""

    issues: list[str] = []
    if not current:
        issues.append("No clear professional summary detected.")
    elif len(current.split()) < 25:
        issues.append("Summary is very short — expand with role focus and key strengths.")
    if current and not any(s.lower() in current.lower() for s in skills[:5]):
        issues.append("Summary does not highlight your strongest technical skills.")
    if current and not has_action_verb(current) and "seeking" not in current.lower():
        issues.append("Summary could use stronger action-oriented language.")
    if current and len(current.split()) > 120:
        issues.append("Summary is lengthy — aim for 3–5 concise sentences.")

    person = name or "This candidate"
    top_skills = ", ".join(skills[:5]) if skills else "relevant technologies"
    improved = (
        f"{person} is a motivated software professional with hands-on experience in {top_skills}. "
        f"Skilled at building practical applications, collaborating in teams, and continuously learning "
        f"modern AI and software engineering practices. Seeking opportunities to apply technical skills "
        f"to deliver measurable impact."
    )

    return SummaryAnalysis(
        current_summary=current or "No summary found in the resume.",
        issues_detected=issues or ["Summary looks reasonable; consider adding measurable outcomes."],
        improved_summary=improved,
    )


def analyze_projects(text: str, skills: list[str]) -> list[ProjectItem]:
    """Detect project entries and attach suggestions."""
    block = find_section_block(text, ["projects", "personal projects", "academic projects"])
    if not block:
        return []

    lines = split_lines(block)[1:]  # skip heading
    projects: list[ProjectItem] = []
    current_name = ""
    current_desc: list[str] = []
    current_tech: list[str] = []

    def flush():
        nonlocal current_name, current_desc, current_tech
        if not current_name and not current_desc:
            return
        name = current_name or (current_desc[0][:60] if current_desc else "Untitled Project")
        desc = " ".join(current_desc)
        strengths = []
        improvements = []
        if current_tech:
            strengths.append("Technologies clearly associated with the project.")
        if has_action_verb(desc):
            strengths.append("Uses action-oriented language.")
        if has_quantifiable(desc):
            strengths.append("Includes measurable results.")
        else:
            improvements.append("Add measurable results (users, accuracy, performance, time saved).")
        if len(desc) < 40:
            improvements.append("Expand the description to explain the problem, approach, and outcome.")
        if not current_tech:
            improvements.append("List the key technologies used.")
        if "architecture" not in desc.lower() and "system" not in desc.lower():
            improvements.append("Briefly explain the technical architecture or design choices.")
        projects.append(
            ProjectItem(
                name=name[:80],
                technologies=current_tech or [s for s in skills if s.lower() in desc.lower()][:5],
                description=desc[:500],
                strengths=strengths or ["Project entry detected."],
                improvements=improvements or ["Polish wording for clarity and impact."],
            )
        )
        current_name = ""
        current_desc = []
        current_tech = []

    for line in lines:
        # New project often starts as a short title-like line
        if len(line) < 70 and not line.endswith(".") and not line.lower().startswith(("tech", "tools", "-")):
            if current_name or current_desc:
                flush()
            current_name = line
            # Detect inline tech
            current_tech = [s.name for s in SKILL_CATALOG if s.name.lower() in line.lower()]
        else:
            current_desc.append(line)
            for s in SKILL_CATALOG:
                if s.name.lower() in line.lower() and s.name not in current_tech:
                    current_tech.append(s.name)

    flush()
    return projects[:8]


def analyze_experience(text: str, skills: list[str]) -> list[ExperienceItem]:
    """Parse experience bullets and score writing quality signals."""
    block = find_section_block(
        text,
        ["experience", "work experience", "employment", "professional experience"],
    )
    if not block:
        return []

    lines = split_lines(block)[1:]
    experiences: list[ExperienceItem] = []
    current = ExperienceItem()

    def flush():
        nonlocal current
        if not current.company and not current.role and not current.responsibilities:
            return
        blob = " ".join(current.responsibilities)
        current.has_action_verbs = any(has_action_verb(r) for r in current.responsibilities) or has_action_verb(blob)
        current.has_technical_skills = bool(current.skills) or any(
            s.lower() in blob.lower() for s in skills[:10]
        )
        current.has_quantifiable_results = any(has_quantifiable(r) for r in current.responsibilities)

        improvements = []
        if not current.has_action_verbs:
            improvements.append("Start bullets with strong action verbs (Built, Developed, Optimized).")
        if not current.has_technical_skills:
            improvements.append("Mention specific technologies used in each role.")
        if not current.has_quantifiable_results:
            improvements.append("Add quantifiable results where possible (%, count, time saved).")
        if not current.responsibilities:
            improvements.append("Add clear responsibility bullets for this role.")
        current.improvements = improvements or ["Experience entry looks solid — keep refining metrics."]
        experiences.append(current)
        current = ExperienceItem()

    for line in lines:
        # Duration patterns
        if re.search(r"(20\d{2}|present|current)", line, re.I) and (
            re.search(r"[-–—]|to", line, re.I) or len(line) < 40
        ):
            if current.role or current.company or current.responsibilities:
                # duration may come after role line
                if not current.duration:
                    current.duration = line
                    continue
                flush()
            current.duration = line
            continue

        # Role / company heuristics
        if len(line) < 80 and not line.endswith(".") and len(current.responsibilities) == 0:
            if not current.role:
                # "Role at Company" or "Role | Company"
                parts = re.split(r"\s+at\s+|\s*\|\s*|\s+-\s+", line, maxsplit=1, flags=re.I)
                if len(parts) == 2:
                    current.role = parts[0].strip()
                    current.company = parts[1].strip()
                else:
                    current.role = line
            elif not current.company:
                current.company = line
            else:
                current.responsibilities.append(line)
        else:
            current.responsibilities.append(line)
            for s in skills:
                if s.lower() in line.lower() and s not in current.skills:
                    current.skills.append(s)

    flush()
    return experiences[:8]


def analyze_education(text: str) -> list[EducationItem]:
    block = find_section_block(text, ["education", "academic background", "academic"])
    if not block:
        return []
    lines = split_lines(block)[1:]
    items: list[EducationItem] = []
    for i, line in enumerate(lines[:6]):
        year = ""
        year_match = re.search(r"(20\d{2}|19\d{2})", line)
        if year_match:
            year = year_match.group(0)
        degree = ""
        if re.search(r"(?i)\b(b\.?tech|b\.?e|m\.?tech|m\.?sc|b\.?sc|bachelor|master|mba|phd|diploma)\b", line):
            degree = line
        items.append(
            EducationItem(
                institution=line if not degree else (lines[i + 1] if i + 1 < len(lines) else ""),
                degree=degree or line,
                year=year,
                details=line,
            )
        )
    # Deduplicate loosely
    unique = []
    seen = set()
    for item in items:
        key = (item.degree[:40], item.year)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:4]


def extract_list_section(text: str, headings: list[str]) -> list[str]:
    block = find_section_block(text, headings)
    if not block:
        return []
    return [ln for ln in split_lines(block)[1:] if 3 < len(ln) < 120][:10]


def classify_strong_skills(detected: list[str], text: str) -> list[str]:
    """Skills mentioned multiple times or in experience/projects are 'strong'."""
    lower = normalize_for_match(text)
    strong = []
    for skill in detected:
        count = len(re.findall(rf"(?<![a-z0-9]){re.escape(skill.lower())}(?![a-z0-9])", lower))
        meta = SKILL_LOOKUP.get(skill.lower())
        if count >= 2 or (meta and meta.priority >= 4 and count >= 1):
            strong.append(skill)
    return strong[:12] or detected[:5]


def recommend_skills(detected: list[str], job_skills: Optional[list[str]] = None) -> list[str]:
    """Recommend skills that are missing relative to a role bundle or JD."""
    detected_set = set(detected)
    if job_skills:
        return [s for s in job_skills if s not in detected_set][:10]

    # Infer role bundle from detected skills
    lower_names = {s.lower() for s in detected}
    if lower_names & {"machine learning", "nlp", "generative ai", "artificial intelligence", "llm apis"}:
        bundle = ROLE_RECOMMENDATIONS["ai_ml"]
    elif lower_names & {"selenium", "manual testing", "api testing"}:
        bundle = ROLE_RECOMMENDATIONS["qa"]
    elif lower_names & {"react", "javascript", "node.js"}:
        bundle = ROLE_RECOMMENDATIONS["fullstack"]
    elif lower_names & {"fastapi", "django", "flask", "python"}:
        bundle = ROLE_RECOMMENDATIONS["backend"]
    else:
        bundle = ROLE_RECOMMENDATIONS["default"]

    return [s for s in bundle if s not in detected_set][:8]


def calculate_ats_score(
    sections: list[str],
    skills: list[str],
    experience: list[ExperienceItem],
    projects: list[ProjectItem],
    education: list[EducationItem],
    personal: PersonalInfo,
    job_skills: Optional[list[str]] = None,
) -> tuple[int, ATSBreakdown, SectionScores]:
    """
    Estimated ATS-style score (0–100) using transparent, weighted criteria.
    This is NOT a real ATS vendor score.
    """
    # Keyword relevance (25)
    if job_skills:
        matched = len([s for s in job_skills if s in skills])
        keyword_pts = int(round((matched / max(len(job_skills), 1)) * 25))
    else:
        keyword_pts = min(25, int(len(skills) * 2.2))

    # Skills (20)
    skills_pts = min(20, int(len(skills) * 1.8))

    # Experience (20)
    if experience:
        quality = sum(
            int(e.has_action_verbs) + int(e.has_technical_skills) + int(e.has_quantifiable_results)
            for e in experience
        )
        experience_pts = min(20, 8 + len(experience) * 3 + quality)
    else:
        experience_pts = 4

    # Projects (15)
    if projects:
        projects_pts = min(15, 6 + len(projects) * 3)
    else:
        projects_pts = 3

    # Education (10)
    education_pts = 10 if education else 4

    # Resume structure (10)
    structure_pts = min(10, len(sections) * 1.5)
    contact_bonus = sum(
        bool(x) for x in [personal.email, personal.phone, personal.linkedin or personal.github]
    )
    structure_pts = min(10, int(structure_pts + contact_bonus * 0.5))

    breakdown = ATSBreakdown(
        keyword_relevance=int(keyword_pts),
        skills=int(skills_pts),
        experience=int(experience_pts),
        projects=int(projects_pts),
        education=int(education_pts),
        resume_structure=int(structure_pts),
        total=0,
    )
    breakdown.total = min(
        100,
        breakdown.keyword_relevance
        + breakdown.skills
        + breakdown.experience
        + breakdown.projects
        + breakdown.education
        + breakdown.resume_structure,
    )

    # Section scores as percentages for the dashboard
    section_scores = SectionScores(
        resume_structure=min(100, int(structure_pts / 10 * 100)),
        skills=min(100, int(skills_pts / 20 * 100)),
        experience=min(100, int(experience_pts / 20 * 100)),
        projects=min(100, int(projects_pts / 15 * 100)),
        keywords=min(100, int(keyword_pts / 25 * 100)),
        readability=min(
            100,
            60
            + (10 if experience else 0)
            + (10 if projects else 0)
            + (10 if "Summary" in sections else 0)
            + (10 if personal.email else 0),
        ),
    )
    return breakdown.total, breakdown, section_scores


def generate_recommendations(
    sections: list[str],
    skills: list[str],
    missing: list[str],
    experience: list[ExperienceItem],
    projects: list[ProjectItem],
    summary: SummaryAnalysis,
    personal: PersonalInfo,
    has_job: bool,
) -> list[str]:
    """Produce actionable recommendations grounded in the analysis."""
    recs: list[str] = []

    if summary.issues_detected and "No clear professional summary" in summary.issues_detected[0]:
        recs.append("Add a concise professional summary highlighting your target role and top skills.")
    elif summary.issues_detected:
        recs.append("Improve your professional summary — " + summary.issues_detected[0])

    if "Experience" not in sections:
        recs.append("Add an Experience section with role, company, duration, and impact-focused bullets.")
    else:
        weak_exp = [e for e in experience if e.improvements]
        if any(not e.has_quantifiable_results for e in experience):
            recs.append("Add measurable achievements to your experience section (metrics, scale, outcomes).")
        if any(not e.has_action_verbs for e in experience):
            recs.append("Rewrite experience bullets to start with strong action verbs.")

    if "Projects" not in sections or not projects:
        recs.append("Include 2–3 projects with technologies used and measurable outcomes.")
    else:
        recs.append("Strengthen your project descriptions with architecture details and results.")

    if missing:
        recs.append(f"Consider building familiarity with: {', '.join(missing[:5])}.")

    if has_job:
        recs.append("Include relevant keywords from the job description naturally in your summary and skills.")

    if not personal.linkedin and not personal.github:
        recs.append("Add LinkedIn and/or GitHub links to improve recruiter discoverability.")

    if "Skills" not in sections:
        recs.append("Create a dedicated Skills section grouped by category (languages, frameworks, tools).")

    recs.append("Avoid unnecessary personal information (photo, full address, marital status) for ATS-friendly formatting.")
    recs.append("Use measurable results wherever possible to demonstrate impact.")

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for r in recs:
        if r not in seen:
            seen.add(r)
            unique.append(r)
    return unique[:10]


def run_rule_based_analysis(text: str, job_description: Optional[str] = None) -> dict:
    """
    Full rule-based analysis pipeline.
    Returns a dict matching AnalysisResponse fields (minus analysis_id/filename).
    """
    personal = extract_personal_info(text)
    sections = detect_sections(text)
    skills = detect_skills(text)
    strong = classify_strong_skills(skills, text)
    projects = analyze_projects(text, skills)
    experience = analyze_experience(text, skills)
    education = analyze_education(text)
    certifications = extract_list_section(text, ["certifications", "certificates", "licenses"])
    achievements = extract_list_section(text, ["achievements", "accomplishments", "awards"])
    summary = analyze_summary(text, skills, personal.name)

    job_skills = detect_skills(job_description) if job_description else []
    missing = recommend_skills(skills, job_skills if job_skills else None)
    recommended = missing[:]  # same list for dashboard clarity

    ats_score, breakdown, section_scores = calculate_ats_score(
        sections, skills, experience, projects, education, personal, job_skills or None
    )

    # Job match is computed in job_matcher / ai_service for separation of concerns
    recommendations = generate_recommendations(
        sections,
        skills,
        missing,
        experience,
        projects,
        summary,
        personal,
        has_job=bool(job_description and job_description.strip()),
    )

    return {
        "personal_info": personal,
        "detected_sections": sections,
        "detected_skills": skills,
        "strong_skills": strong,
        "missing_skills": missing,
        "recommended_skills": recommended,
        "ats_score": ats_score,
        "ats_breakdown": breakdown,
        "section_scores": section_scores,
        "recommendations": recommendations,
        "summary_analysis": summary,
        "projects": projects,
        "experience": experience,
        "education": education,
        "certifications": certifications,
        "achievements": achievements,
        "_job_skills": job_skills,
        "_resume_skills": skills,
    }
