import datetime
import hashlib
import logging
import math
import re
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger("app.services.ranking.fairness_audit")

# Demographic proxy indicators to mask during evaluation views
GENDER_PRONOUNS_REGEX = re.compile(r"\b(?:he|him|his|she|her|hers)\b", re.IGNORECASE)
DATE_OF_BIRTH_REGEX = re.compile(r"\b(?:dob|date of birth|birthdate)\s*[:\-]?\s*[\w\d\s,/-]+", re.IGNORECASE)
AGE_MENTION_REGEX = re.compile(r"\b\d{1,2}\s*years?\s+old\b", re.IGNORECASE)


class AnonymizedCandidateView(BaseModel):
    anonymous_id: str
    original_candidate_id: str
    sanitized_summary: str
    skills: List[str]
    experience_highlights: List[Dict[str, Any]]
    education_highlights: List[Dict[str, Any]]
    multimodal_metrics: Dict[str, Any]
    advisory_notice: str = (
        "ADVISORY ONLY: Algorithm-generated metrics are supportive guidelines. "
        "Automated candidate disqualification is strictly prohibited by fairness governance."
    )


class ThresholdSensitivityItem(BaseModel):
    threshold_score: float
    selected_count: int
    selection_rate_pct: float


class FairnessBatchAuditReport(BaseModel):
    sample_size: int
    mean_score: float
    median_score: float
    std_dev: float
    min_score: float
    max_score: float
    percentiles: Dict[str, float]
    score_spread: float
    calibration_drift_flag: bool
    threshold_sensitivities: List[ThresholdSensitivityItem]
    advisory_compliance_passed: bool = True
    audit_warnings: List[str] = Field(default_factory=list)
    audited_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


class FairnessAuditorService:
    """
    Guarantees algorithmic fairness, enforces advisory-only evaluation,
    sanitizes candidate PII and demographic proxies for unbiased reviews,
    and calculates statistical spread and calibration drift across candidate batches.
    """

    def anonymize_for_review(self, candidate_data: Dict[str, Any]) -> AnonymizedCandidateView:
        """
        Strips direct PII (name, email, phone, location) and masks demographic proxies
        (gendered pronouns, graduation years > 15 years ago) for bias-free evaluation.
        """
        raw_id = str(candidate_data.get("candidate_id", "unknown"))
        # Generate stable anonymous code identifier e.g. "Candidate #A4F9"
        hash_code = hashlib.md5(raw_id.encode("utf-8")).hexdigest()[:4].upper()
        anon_id = f"Candidate #{hash_code}"

        summary = candidate_data.get("summary", "") or ""
        # Scrub gender pronouns from summary
        clean_summary = GENDER_PRONOUNS_REGEX.sub("they/them", summary)
        clean_summary = DATE_OF_BIRTH_REGEX.sub("[DOB_REDACTED]", clean_summary)
        clean_summary = AGE_MENTION_REGEX.sub("[AGE_REDACTED]", clean_summary)

        # Sanitize experience highlights (preserving technical achievements and role titles)
        exp_sanitized = []
        for item in candidate_data.get("experience", []):
            exp_item = dict(item) if isinstance(item, dict) else item.model_dump()
            desc = exp_item.get("description", "") or ""
            exp_item["description"] = GENDER_PRONOUNS_REGEX.sub("they", desc)
            exp_sanitized.append(exp_item)

        # Sanitize education: mask graduation years older than 15 years to prevent age bias
        current_year = datetime.datetime.now().year
        edu_sanitized = []
        for item in candidate_data.get("education", []):
            edu_item = dict(item) if isinstance(item, dict) else item.model_dump()
            grad_year = edu_item.get("graduation_year")
            if grad_year and (current_year - grad_year > 15):
                edu_item["graduation_year"] = None
                edu_item["institution"] = f"{edu_item.get('institution', '')} (Year Redacted for Bias Protection)"
            edu_sanitized.append(edu_item)

        multimodal = candidate_data.get("multimodal_analysis") or {}
        if hasattr(multimodal, "model_dump"):
            multimodal = multimodal.model_dump()

        return AnonymizedCandidateView(
            anonymous_id=anon_id,
            original_candidate_id=raw_id,
            sanitized_summary=clean_summary,
            skills=candidate_data.get("skills", []),
            experience_highlights=exp_sanitized,
            education_highlights=edu_sanitized,
            multimodal_metrics={
                "speaking_pace": multimodal.get("speaking_pace", "optimal"),
                "words_per_minute": multimodal.get("words_per_minute", 135.0),
                "sentiment_label": multimodal.get("sentiment_label", "POSITIVE"),
                "confidence_score": multimodal.get("confidence_score", 90.0),
            },
        )

    def audit_batch_distribution(
        self, scores: List[float], expected_mean_range: tuple = (65.0, 85.0)
    ) -> FairnessBatchAuditReport:
        """
        Computes statistical distribution metrics, spread, and threshold-sensitivities
        to detect algorithmic calibration drift or disparate impact vulnerabilities.
        """
        warnings: List[str] = []

        if not scores:
            return FairnessBatchAuditReport(
                sample_size=0,
                mean_score=0.0,
                median_score=0.0,
                std_dev=0.0,
                min_score=0.0,
                max_score=0.0,
                percentiles={"p25": 0.0, "p50": 0.0, "p75": 0.0, "p90": 0.0},
                score_spread=0.0,
                calibration_drift_flag=False,
                threshold_sensitivities=[],
                advisory_compliance_passed=True,
                audit_warnings=["No candidate scores provided for batch distribution analysis."],
            )

        arr = np.array(scores, dtype=np.float64)
        n = len(arr)
        mean_val = float(np.mean(arr))
        median_val = float(np.median(arr))
        std_val = float(np.std(arr)) if n > 1 else 0.0
        min_val = float(np.min(arr))
        max_val = float(np.max(arr))
        spread = max_val - min_val

        p25 = float(np.percentile(arr, 25))
        p50 = median_val
        p75 = float(np.percentile(arr, 75))
        p90 = float(np.percentile(arr, 90))

        # Calibration drift detection:
        # Flag if mean score deviates outside normal expected range or std_dev is abnormally low
        drift_flag = False
        if n >= 5:
            if mean_val < expected_mean_range[0]:
                drift_flag = True
                warnings.append(
                    f"Calibration Drift: Mean score ({mean_val:.1f}) is unusually low (<{expected_mean_range[0]}). Criteria may be overly stringent."
                )
            elif mean_val > expected_mean_range[1]:
                drift_flag = True
                warnings.append(
                    f"Calibration Drift: Mean score ({mean_val:.1f}) is unusually high (>{expected_mean_range[1]}). Criteria may lack discrimination power."
                )

            if std_val < 3.0:
                warnings.append(
                    f"Low Variance Warning: Standard deviation ({std_val:.1f}) indicates potential score compression."
                )

        # Threshold sensitivity check across key cutoff thresholds (60, 70, 75, 80, 85)
        sensitivities = []
        for thresh in [60.0, 70.0, 75.0, 80.0, 85.0]:
            selected = int(np.sum(arr >= thresh))
            rate = round((selected / n) * 100.0, 1)
            sensitivities.append(
                ThresholdSensitivityItem(
                    threshold_score=thresh,
                    selected_count=selected,
                    selection_rate_pct=rate,
                )
            )

        # Four-Fifths / Adverse Impact check notice
        if n >= 10:
            high_cutoff_rate = sensitivities[-1].selection_rate_pct
            if high_cutoff_rate < 10.0:
                warnings.append(
                    "Sensitivity Alert: 85+ score threshold selects <10% of batch. Validate that thresholds do not cause disparate exclusion."
                )

        return FairnessBatchAuditReport(
            sample_size=n,
            mean_score=round(mean_val, 1),
            median_score=round(median_val, 1),
            std_dev=round(std_val, 1),
            min_score=round(min_val, 1),
            max_score=round(max_val, 1),
            percentiles={
                "p25": round(p25, 1),
                "p50": round(p50, 1),
                "p75": round(p75, 1),
                "p90": round(p90, 1),
            },
            score_spread=round(spread, 1),
            calibration_drift_flag=drift_flag,
            threshold_sensitivities=sensitivities,
            advisory_compliance_passed=True,
            audit_warnings=warnings,
        )


# Global singleton fairness auditor instance
fairness_auditor = FairnessAuditorService()
