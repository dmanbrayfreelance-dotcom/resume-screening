import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.services.nlp.matcher import MatchEvaluationResult
from backend.app.services.multimodal.sentiment_analyzer import SentimentAnalysisResult
from backend.app.services.multimodal.prosody_vision import ProsodyVisionResult
from backend.app.services.multimodal.claim_verifier import ClaimVerificationResult

logger = logging.getLogger("app.services.ranking.hybrid_scorer")

DEFAULT_WEIGHTS = {
    "skill_match": 0.35,
    "experience_match": 0.25,
    "multimodal_presentation": 0.15,
    "sentiment_engagement": 0.10,
    "claim_credibility": 0.15,
}


class ScoreComponent(BaseModel):
    name: str
    raw_score: float = Field(..., ge=0.0, le=100.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    weighted_score: float = Field(..., ge=0.0, le=100.0)
    status: str = Field(..., description="Excellent, Strong, Moderate, Needs Review")
    details: str


class HybridScoreResult(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0)
    recommendation: str = Field(
        ...,
        description="Strong Hire, Hire, Further Review, Hold / Revisit, Consider Alternate Role",
    )
    is_advisory_only: bool = Field(default=True, description="Strict compliance: Never auto-rejects")
    components: Dict[str, ScoreComponent]
    strengths: List[str] = Field(default_factory=list)
    areas_for_probing: List[str] = Field(default_factory=list)
    recruiter_executive_summary: str


class HybridScorerService:
    """
    Ranks candidates by synthesizing section-weighted semantic similarity,
    skill coverage, speech prosody, video sentiment, and cross-modal claim credibility.
    Produces a transparent, non-black-box score breakdown with recruiter action items.
    """

    def score_candidate(
        self,
        candidate_name: str,
        job_title: str,
        semantic_match: MatchEvaluationResult,
        sentiment: SentimentAnalysisResult,
        prosody: ProsodyVisionResult,
        claim_verification: ClaimVerificationResult,
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> HybridScoreResult:
        """
        Synthesizes multi-modal screening components into an explainable composite scorecard.
        """
        weights = dict(DEFAULT_WEIGHTS)
        if custom_weights:
            weights.update(custom_weights)

        # Normalize weights to sum to 1.0
        total_w = sum(weights.values())
        if total_w <= 0:
            total_w = 1.0
        norm_weights = {k: v / total_w for k, v in weights.items()}

        # 1. Component Raw Scores (0 to 100)
        skill_score = semantic_match.section_scores.get("skills", 75.0)
        exp_score = semantic_match.section_scores.get("experience", 75.0)
        pres_score = prosody.overall_presentation_score
        sent_score = sentiment.polarity_score * 100.0
        cred_score = claim_verification.credibility_score

        components: Dict[str, ScoreComponent] = {
            "skill_match": ScoreComponent(
                name="Skill Coverage & Overlap",
                raw_score=round(skill_score, 1),
                weight=round(norm_weights["skill_match"], 3),
                weighted_score=round(skill_score * norm_weights["skill_match"], 2),
                status=self._get_status(skill_score),
                details=f"{semantic_match.skill_gap.coverage_pct}% required skill coverage ({len(semantic_match.skill_gap.matched_skills)} matched).",
            ),
            "experience_match": ScoreComponent(
                name="Career Experience & Semantics",
                raw_score=round(exp_score, 1),
                weight=round(norm_weights["experience_match"], 3),
                weighted_score=round(exp_score * norm_weights["experience_match"], 2),
                status=self._get_status(exp_score),
                details=f"Semantic experience fit score: {exp_score:.1f}/100.",
            ),
            "multimodal_presentation": ScoreComponent(
                name="Speech Delivery & Visual Engagement",
                raw_score=round(pres_score, 1),
                weight=round(norm_weights["multimodal_presentation"], 3),
                weighted_score=round(pres_score * norm_weights["multimodal_presentation"], 2),
                status=self._get_status(pres_score),
                details=f"Pace: {prosody.speaking_pace} ({prosody.words_per_minute:.0f} WPM), filler ratio: {prosody.filler_word_ratio*100:.1f}%.",
            ),
            "sentiment_engagement": ScoreComponent(
                name="Interview Sentiment & Tone",
                raw_score=round(sent_score, 1),
                weight=round(norm_weights["sentiment_engagement"], 3),
                weighted_score=round(sent_score * norm_weights["sentiment_engagement"], 2),
                status=self._get_status(sent_score),
                details=f"Tone: {sentiment.label} ({sentiment.polarity_score:.2f} polarity).",
            ),
            "claim_credibility": ScoreComponent(
                name="Cross-Modal Claim Consistency",
                raw_score=round(cred_score, 1),
                weight=round(norm_weights["claim_credibility"], 3),
                weighted_score=round(cred_score * norm_weights["claim_credibility"], 2),
                status=self._get_status(cred_score),
                details=f"{len(claim_verification.aligned)} aligned claims, {len(claim_verification.potential_discrepancy)} flagged discrepancies.",
            ),
        }

        # Composite Score Calculation
        overall = sum(c.weighted_score for c in components.values())
        overall = max(0.0, min(100.0, round(overall, 1)))

        # Recommendation Rubric (Advisory only)
        if overall >= 88.0:
            recommendation = "Strong Hire"
        elif overall >= 75.0:
            recommendation = "Hire"
        elif overall >= 62.0:
            recommendation = "Further Review"
        elif overall >= 50.0:
            recommendation = "Hold / Revisit"
        else:
            recommendation = "Consider Alternate Role"

        # Generate Strengths & Areas for Probing
        strengths, probing = self._generate_explainability(
            semantic_match, sentiment, prosody, claim_verification
        )

        exec_summary = (
            f"{candidate_name} evaluated for '{job_title}' with composite fit score of {overall:.1f}/100 "
            f"({recommendation}). Demonstrates {semantic_match.skill_gap.coverage_pct:.0f}% skill coverage with "
            f"{prosody.speaking_pace} verbal articulation and {claim_verification.credibility_score:.0f}/100 claim credibility."
        )

        return HybridScoreResult(
            overall_score=overall,
            recommendation=recommendation,
            is_advisory_only=True,
            components=components,
            strengths=strengths,
            areas_for_probing=probing,
            recruiter_executive_summary=exec_summary,
        )

    def _get_status(self, score: float) -> str:
        if score >= 88.0:
            return "Excellent"
        elif score >= 75.0:
            return "Strong"
        elif score >= 60.0:
            return "Moderate"
        else:
            return "Needs Review"

    def _generate_explainability(
        self,
        semantic_match: MatchEvaluationResult,
        sentiment: SentimentAnalysisResult,
        prosody: ProsodyVisionResult,
        claim_verification: ClaimVerificationResult,
    ) -> Tuple[List[str], List[str]]:
        """Generates actionable bullet points for recruiter interview preparation."""
        strengths = []
        probing = []

        # Skills & Experience
        if semantic_match.skill_gap.coverage_pct >= 75.0:
            strengths.append(
                f"High core skill coverage ({semantic_match.skill_gap.coverage_pct:.0f}%) matching key requirements."
            )
        if semantic_match.skill_gap.missing_required_skills:
            missing_str = ", ".join(semantic_match.skill_gap.missing_required_skills[:3])
            probing.append(f"Probe hands-on proficiency in missing required skills: {missing_str}.")

        # Presentation & Delivery
        if prosody.speaking_pace == "optimal" and prosody.filler_word_ratio < 0.03:
            strengths.append(
                f"Articulate verbal presentation with optimal cadence ({prosody.words_per_minute:.0f} WPM) and minimal filler words."
            )
        elif prosody.filler_word_ratio > 0.05:
            probing.append(
                f"Noticeable verbal hesitation ({prosody.filler_word_ratio*100:.1f}% filler words). Test candidate under live technical questioning."
            )

        # Sentiment & Tone
        if sentiment.label == "POSITIVE":
            strengths.append(
                f"Strong professional enthusiasm and constructive problem-solving tone ({sentiment.polarity_score:.2f} polarity)."
            )

        # Credibility & Cross-modal alignment
        if claim_verification.potential_discrepancy:
            for disc in claim_verification.potential_discrepancy:
                probing.append(f"Investigate timeline/role assertion: {disc.explanation}")
        elif len(claim_verification.aligned) >= 3:
            strengths.append(
                f"High cross-modal consistency ({len(claim_verification.aligned)} competencies independently verified in both speech and resume)."
            )

        return strengths[:4], probing[:4]


# Global singleton hybrid scorer instance
hybrid_scorer = HybridScorerService()
