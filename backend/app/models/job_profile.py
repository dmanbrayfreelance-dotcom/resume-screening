import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ScoringWeights(BaseModel):
    """Configurable weights for ranking candidates against this job profile."""

    skill_match: float = Field(default=0.35, ge=0.0, le=1.0)
    experience_match: float = Field(default=0.25, ge=0.0, le=1.0)
    multimodal_presentation: float = Field(default=0.15, ge=0.0, le=1.0)
    sentiment_engagement: float = Field(default=0.10, ge=0.0, le=1.0)
    claim_credibility: float = Field(default=0.15, ge=0.0, le=1.0)

    model_config = ConfigDict(extra="allow")


class JobProfileBase(BaseModel):
    title: str = Field(..., description="Job Title, e.g. Senior Multimodal AI Engineer")
    department: str = Field(default="Engineering")
    location: str = Field(default="Remote / Hybrid")
    employment_type: str = Field(default="Full-time")
    experience_years_min: float = Field(default=2.0, ge=0)
    experience_years_max: Optional[float] = Field(default=None)
    education_level: str = Field(default="Bachelor's Degree or Equivalent")
    description: str = Field(..., description="Detailed role overview")
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    scoring_weights: ScoringWeights = Field(default_factory=ScoringWeights)
    status: str = Field(default="open", description="open, draft, closed, archived")


class JobProfileCreate(JobProfileBase):
    pass


class JobProfileUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_years_min: Optional[float] = None
    experience_years_max: Optional[float] = None
    education_level: Optional[str] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    scoring_weights: Optional[ScoringWeights] = None
    status: Optional[str] = None


class JobProfile(JobProfileBase):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "job-101",
                "title": "Senior AI / ML Research Engineer",
                "department": "AI Labs",
                "location": "San Francisco, CA (Hybrid)",
                "employment_type": "Full-time",
                "experience_years_min": 4.0,
                "experience_years_max": 8.0,
                "education_level": "Master's or Ph.D. preferred",
                "description": "Leading research and productionization of multimodal LLMs and computer vision pipelines.",
                "responsibilities": [
                    "Design and deploy multimodal inference architectures",
                    "Fine-tune Whisper and LLM foundation models",
                    "Collaborate with product and frontend engineering teams"
                ],
                "required_skills": ["Python", "PyTorch", "FastAPI", "MongoDB", "Whisper", "Transformers"],
                "preferred_skills": ["Docker", "Kubernetes", "CUDA", "TensorRT"],
                "scoring_weights": {
                    "skill_match": 0.40,
                    "experience_match": 0.25,
                    "multimodal_presentation": 0.20,
                    "sentiment_engagement": 0.15
                },
                "status": "open"
            }
        }
    )
