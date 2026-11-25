import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactInfo(BaseModel):
    name: str = Field(..., description="Full candidate name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    linkedin_url: Optional[str] = Field(default=None)
    github_url: Optional[str] = Field(default=None)
    portfolio_url: Optional[str] = Field(default=None)


class ExperienceItem(BaseModel):
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    duration_months: Optional[int] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class MultimodalAnalysis(BaseModel):
    """Speech, video, tone, speaking pace, and sentiment analysis."""

    video_filename: Optional[str] = None
    audio_extracted_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    transcript: Optional[str] = None
    words_per_minute: Optional[float] = None
    speaking_pace: Optional[str] = Field(default=None, description="slow, optimal, fast")
    sentiment_label: Optional[str] = Field(default=None, description="POSITIVE, NEUTRAL, NEGATIVE")
    sentiment_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    clarity_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    engagement_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    flagged_anomalies: List[str] = Field(default_factory=list)


class EvaluationScore(BaseModel):
    """Job-specific fit evaluation score and breakdown."""

    job_id: str
    overall_fit_score: float = Field(..., ge=0.0, le=100.0)
    skill_match_score: float = Field(..., ge=0.0, le=100.0)
    experience_score: float = Field(..., ge=0.0, le=100.0)
    presentation_score: float = Field(..., ge=0.0, le=100.0)
    sentiment_score: float = Field(..., ge=0.0, le=100.0)
    recommendation: str = Field(..., description="Strong Hire, Hire, Review, Reject")
    match_summary: str
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FairnessAuditMetadata(BaseModel):
    """Ensures bias prevention, audit logging, and equal opportunity tracking."""

    anonymized_view_enabled: bool = True
    bias_check_passed: bool = True
    demographic_parity_flag: bool = False
    audit_notes: Optional[str] = None
    last_audited_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CandidateBase(BaseModel):
    contact_info: ContactInfo
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    raw_resume_text: Optional[str] = None
    resume_file_url: Optional[str] = None
    status: str = Field(default="applied", description="applied, screened, shortlisted, rejected")


class CandidateCreate(CandidateBase):
    pass


class Candidate(CandidateBase):
    candidate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    multimodal_analysis: Optional[MultimodalAnalysis] = None
    evaluations: List[EvaluationScore] = Field(default_factory=list)
    fairness_metadata: FairnessAuditMetadata = Field(default_factory=FairnessAuditMetadata)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "candidate_id": "cand-001",
                "contact_info": {
                    "name": "Sarah Chen",
                    "email": "sarah.chen@example.com",
                    "phone": "+1-555-0199",
                    "location": "Seattle, WA",
                    "github_url": "https://github.com/sarahchen-ai"
                },
                "summary": "AI Engineer with 5+ years building production multimodal models and FastAPI microservices.",
                "skills": ["Python", "PyTorch", "FastAPI", "Whisper", "MongoDB", "Transformers", "Docker"],
                "status": "screened"
            }
        }
    )