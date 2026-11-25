import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.services.nlp.skill_extractor import skill_extractor

logger = logging.getLogger("app.services.multimodal.claim_verifier")


class DiscrepancyItem(BaseModel):
    category: str = Field(..., description="experience_tenure, role_seniority, skill_claim")
    claim_in_video: str
    claim_in_resume: str
    severity: str = Field(..., description="low, medium, high")
    explanation: str


class ClaimVerificationResult(BaseModel):
    credibility_score: float = Field(..., ge=0.0, le=100.0)
    aligned: List[str] = Field(
        default_factory=list,
        description="Skills and competencies confirmed in both resume and spoken interview",
    )
    mentioned_only_in_video: List[str] = Field(
        default_factory=list,
        description="Competencies articulated verbally but absent from the written resume",
    )
    mentioned_only_in_resume: List[str] = Field(
        default_factory=list,
        description="Competencies on written resume not touched upon verbally",
    )
    potential_discrepancy: List[DiscrepancyItem] = Field(
        default_factory=list,
        description="Contradictions in tenure, title, or seniority between resume and speech",
    )
    recruiter_notes: List[str] = Field(default_factory=list)


SENIORITY_RANKS = {
    "intern": 1,
    "junior": 2,
    "associate": 2,
    "mid-level": 3,
    "software engineer": 3,
    "developer": 3,
    "senior": 4,
    "lead": 5,
    "tech lead": 5,
    "technical lead": 5,
    "staff": 6,
    "engineering manager": 6,
    "principal": 7,
    "director": 8,
    "vp": 9,
    "vp of engineering": 9,
    "cto": 10,
    "chief technology officer": 10,
    "ceo": 10,
    "chief executive officer": 10,
}


class MultimodalClaimVerifierService:
    """
    Cross-checks candidate statements articulated in video transcripts against written resumes.
    Flags discrepancies in experience duration, seniority claims, and verified technical skills.
    """

    def verify_claims(
        self,
        resume_text: str,
        video_transcript: str,
        known_resume_skills: Optional[List[str]] = None,
    ) -> ClaimVerificationResult:
        """
        Cross-examines spoken statements against written resume records.
        """
        discrepancies: List[DiscrepancyItem] = []
        recruiter_notes: List[str] = []

        # 1. Extract skills from Resume and Video Transcript
        if known_resume_skills:
            resume_skills_set = set(known_resume_skills)
        else:
            res_extracted = skill_extractor.extract_skills(resume_text)
            resume_skills_set = set(res_extracted.all_skills)

        vid_extracted = skill_extractor.extract_skills(video_transcript)
        video_skills_set = set(vid_extracted.all_skills)

        # Categorize skill overlaps
        aligned_skills = sorted(list(resume_skills_set.intersection(video_skills_set)))
        only_video = sorted(list(video_skills_set.difference(resume_skills_set)))
        only_resume = sorted(list(resume_skills_set.difference(video_skills_set)))

        # 2. Cross-check Experience Tenure Claims
        res_years = skill_extractor._extract_experience_years(resume_text)
        vid_years = skill_extractor._extract_experience_years(video_transcript)

        if res_years is not None and vid_years is not None:
            diff = abs(vid_years - res_years)
            if vid_years > res_years + 2.0:
                # Video claims significantly more years than written on resume
                discrepancy = DiscrepancyItem(
                    category="experience_tenure",
                    claim_in_video=f"Claimed {vid_years:.1f} years of experience in video interview",
                    claim_in_resume=f"Written resume documents {res_years:.1f} years of experience",
                    severity="high" if diff > 3.0 else "medium",
                    explanation=(
                        f"Candidate stated {vid_years:.1f} years verbally, which exceeds the "
                        f"{res_years:.1f} years documented in the written work history by {diff:.1f} years."
                    ),
                )
                discrepancies.append(discrepancy)
                recruiter_notes.append(
                    f"Clarify experience timeline: Spoken claim ({vid_years:.1f} yrs) exceeds written history ({res_years:.1f} yrs)."
                )
            elif vid_years < res_years - 3.0:
                recruiter_notes.append(
                    f"Candidate focused verbal discussion on recent {vid_years:.1f} years out of {res_years:.1f} total years."
                )

        # 3. Cross-check Seniority and Leadership Claims
        video_lower = video_transcript.lower()
        resume_lower = resume_text.lower()

        for title, rank in SENIORITY_RANKS.items():
            if rank >= 5:  # Lead, Staff, Principal, Director, VP, CTO
                pattern = rf"\b(?:as|was|served as|promoted to)?\s*(?:the\s+)?{re.escape(title)}\b"
                if re.search(pattern, video_lower):
                    # Check if title appears in resume
                    if not re.search(rf"\b{re.escape(title)}\b", resume_lower):
                        discrepancies.append(
                            DiscrepancyItem(
                                category="role_seniority",
                                claim_in_video=f"Claimed '{title.title()}' role in verbal discussion",
                                claim_in_resume=f"Title '{title.title()}' not found in written employment history",
                                severity="medium",
                                explanation=(
                                    f"Candidate referred to serving in a '{title.title()}' capacity in video, "
                                    "but this exact title does not appear in the written job history."
                                ),
                            )
                        )
                        recruiter_notes.append(
                            f"Confirm leadership scope: Candidate mentioned '{title.title()}' responsibilities in interview."
                        )

        # 4. Compute Credibility Index (0 to 100)
        # Base starts at 90.0
        # Positive boost for high alignment ratio
        # Penalties for discrepancies based on severity
        total_unique_skills = max(len(resume_skills_set.union(video_skills_set)), 1)
        alignment_ratio = len(aligned_skills) / total_unique_skills

        credibility = 80.0 + (alignment_ratio * 18.0)

        for d in discrepancies:
            if d.severity == "high":
                credibility -= 20.0
            elif d.severity == "medium":
                credibility -= 10.0
            else:
                credibility -= 5.0

        if only_video:
            recruiter_notes.append(
                f"Candidate introduced additional competencies during interview not in resume: {', '.join(only_video[:4])}."
            )

        credibility = max(10.0, min(100.0, round(credibility, 1)))

        return ClaimVerificationResult(
            credibility_score=credibility,
            aligned=aligned_skills,
            mentioned_only_in_video=only_video,
            mentioned_only_in_resume=only_resume,
            potential_discrepancy=discrepancies,
            recruiter_notes=recruiter_notes,
        )


# Global singleton claim verifier instance
claim_verifier = MultimodalClaimVerifierService()
