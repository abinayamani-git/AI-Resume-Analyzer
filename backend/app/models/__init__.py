"""
Pydantic models for API request/response validation.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None


class ProjectItem(BaseModel):
    name: str
    technologies: list[str] = []
    description: str = ""
    strengths: list[str] = []
    improvements: list[str] = []


class ExperienceItem(BaseModel):
    company: str = ""
    role: str = ""
    duration: str = ""
    skills: list[str] = []
    responsibilities: list[str] = []
    has_action_verbs: bool = False
    has_technical_skills: bool = False
    has_quantifiable_results: bool = False
    improvements: list[str] = []


class EducationItem(BaseModel):
    institution: str = ""
    degree: str = ""
    year: str = ""
    details: str = ""


class SectionScores(BaseModel):
    resume_structure: int = 0
    skills: int = 0
    experience: int = 0
    projects: int = 0
    keywords: int = 0
    readability: int = 0


class ATSBreakdown(BaseModel):
    keyword_relevance: int = 0
    skills: int = 0
    experience: int = 0
    projects: int = 0
    education: int = 0
    resume_structure: int = 0
    total: int = 0


class SummaryAnalysis(BaseModel):
    current_summary: str = ""
    issues_detected: list[str] = []
    improved_summary: str = ""


class JobMatchResult(BaseModel):
    job_match_percentage: Optional[int] = None
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    important_keywords: list[str] = []
    recommended_skills: list[str] = []
    experience_alignment: str = ""
    project_alignment: str = ""
    explanation: str = ""


class AnalyzeRequest(BaseModel):
    """Request body for resume analysis."""
    file_id: str = Field(..., description="ID returned from /api/upload")
    job_description: Optional[str] = Field(None, description="Optional job description text")


class JobMatchRequest(BaseModel):
    """Standalone job-match request."""
    file_id: str
    job_description: str


class AnalysisResponse(BaseModel):
    """Full analysis payload returned to the frontend dashboard."""
    analysis_id: str
    filename: str
    analysis_mode: str = "fallback"  # "fallback" or "llm"
    personal_info: PersonalInfo
    detected_sections: list[str] = []
    detected_skills: list[str] = []
    strong_skills: list[str] = []
    missing_skills: list[str] = []
    recommended_skills: list[str] = []
    ats_score: int = 0
    ats_breakdown: ATSBreakdown
    section_scores: SectionScores
    job_match: JobMatchResult
    recommendations: list[str] = []
    summary_analysis: SummaryAnalysis
    projects: list[ProjectItem] = []
    experience: list[ExperienceItem] = []
    education: list[EducationItem] = []
    certifications: list[str] = []
    achievements: list[str] = []
    message: str = "Analysis complete"


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    message: str
    size_bytes: int


class HealthResponse(BaseModel):
    status: str
    app: str
    ai_provider: str


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class ReportMeta(BaseModel):
    analysis_id: str
    available: bool
    message: str = ""
