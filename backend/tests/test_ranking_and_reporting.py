import csv
import io
import json
import pytest
from backend.app.services.ranking.hybrid_scorer import hybrid_scorer
from backend.app.services.ranking.fairness_audit import fairness_auditor
from backend.app.services.reporting.exporter import reporting_exporter
from backend.app.services.nlp.matcher import MatchEvaluationResult, SkillGapReport
from backend.app.services.multimodal.sentiment_analyzer import SentimentAnalysisResult
from backend.app.services.multimodal.prosody_vision import ProsodyVisionResult
from backend.app.services.multimodal.claim_verifier import ClaimVerificationResult, DiscrepancyItem


@pytest.fixture
def mock_evaluation_components():
    semantic_match = MatchEvaluationResult(
        overall_fit_score=86.0,
        section_scores={"skills": 88.0, "experience": 85.0, "education": 90.0, "semantic_fit": 84.0},
        skill_gap=SkillGapReport(
            matched_skills=["Python", "FastAPI", "Whisper", "MongoDB"],
            missing_required_skills=["PyTorch"],
            missing_preferred_skills=["Docker"],
            coverage_pct=80.0,
            recommendations=["Build PyTorch multimodal project."],
        ),
        fit_summary="Strong match for Senior AI Engineer.",
    )

    sentiment = SentimentAnalysisResult(
        label="POSITIVE",
        polarity_score=0.88,
        positive_prob=0.88,
        neutral_prob=0.10,
        negative_prob=0.02,
        confidence=92.0,
    )

    prosody = ProsodyVisionResult(
        speaking_pace="optimal",
        words_per_minute=138.0,
        filler_word_ratio=0.015,
        vocal_energy_score=88.0,
        pitch_stability_score=90.0,
        visual_engagement_score=89.0,
        eye_contact_stability=90.0,
        overall_presentation_score=91.5,
    )

    claim_verification = ClaimVerificationResult(
        credibility_score=94.0,
        aligned=["Python", "FastAPI", "Whisper"],
        mentioned_only_in_video=["LangChain"],
        mentioned_only_in_resume=["MongoDB"],
        potential_discrepancy=[],
        recruiter_notes=["Candidate articulated additional LangChain experience."],
    )

    return semantic_match, sentiment, prosody, claim_verification


def test_hybrid_scorer_breakdown_and_explainability(mock_evaluation_components):
    """Verify hybrid scoring, transparent breakdown, and advisory-only compliance."""
    sem, sent, pros, claim = mock_evaluation_components

    result = hybrid_scorer.score_candidate(
        candidate_name="Sarah Chen",
        job_title="Senior Multimodal AI Engineer",
        semantic_match=sem,
        sentiment=sent,
        prosody=pros,
        claim_verification=claim,
    )

    assert 80.0 <= result.overall_score <= 100.0
    assert result.is_advisory_only is True
    assert result.recommendation in ["Strong Hire", "Hire"]

    # Verify transparent component breakdown
    assert "skill_match" in result.components
    assert "experience_match" in result.components
    assert "multimodal_presentation" in result.components
    assert "sentiment_engagement" in result.components
    assert "claim_credibility" in result.components

    # Verify status and details are present
    assert result.components["skill_match"].status in ["Strong", "Excellent"]
    assert len(result.strengths) > 0
    assert "Sarah Chen" in result.recruiter_executive_summary


def test_fairness_auditor_anonymization_and_batch_distribution():
    """Verify PII stripping, proxy neutralization, and statistical drift checks."""
    candidate_profile = {
        "candidate_id": "cand-001",
        "contact_info": {
            "name": "Sarah Chen",
            "email": "sarah.chen@example.com",
            "phone": "+1-555-0192",
            "location": "San Francisco, CA",
        },
        "summary": "She is an AI engineer. Her focus has been multimodal deep learning.",
        "skills": ["Python", "FastAPI", "Whisper"],
        "experience": [{"role": "Senior Engineer", "company": "AI Labs", "description": "She scaled the platform."}],
        "education": [{"institution": "UC Berkeley", "degree": "BS", "graduation_year": 2002}],
        "multimodal_analysis": {"speaking_pace": "optimal", "words_per_minute": 140.0},
    }

    anon_view = fairness_auditor.anonymize_for_review(candidate_profile)

    assert "Candidate #" in anon_view.anonymous_id
    assert "sarah.chen@example.com" not in anon_view.sanitized_summary
    assert "She" not in anon_view.sanitized_summary
    assert "they" in anon_view.sanitized_summary.lower()
    # Check graduation year > 15 years was masked
    assert anon_view.education_highlights[0]["graduation_year"] is None
    assert "Bias Protection" in anon_view.education_highlights[0]["institution"]
    assert "ADVISORY ONLY" in anon_view.advisory_notice

    # Batch statistical distribution test
    scores = [78.5, 82.0, 91.0, 68.0, 74.0, 88.0, 79.0, 85.0, 72.0, 95.0]
    batch_audit = fairness_auditor.audit_batch_distribution(scores)

    assert batch_audit.sample_size == 10
    assert 75.0 <= batch_audit.mean_score <= 85.0
    assert batch_audit.calibration_drift_flag is False
    assert len(batch_audit.threshold_sensitivities) == 5
    assert batch_audit.advisory_compliance_passed is True

    # Test drift trigger on heavily deflated batch
    deflated_scores = [35.0, 42.0, 38.0, 45.0, 40.0, 39.0]
    drift_audit = fairness_auditor.audit_batch_distribution(deflated_scores)
    assert drift_audit.calibration_drift_flag is True
    assert any("Calibration Drift" in w for w in drift_audit.audit_warnings)


def test_reporting_exporter_csv_and_json(mock_evaluation_components):
    """Verify CSV and JSON exporting for shortlists, breakdowns, and fairness audits."""
    sem, sent, pros, claim = mock_evaluation_components

    hybrid_res = hybrid_scorer.score_candidate(
        candidate_name="Sarah Chen",
        job_title="Senior Multimodal AI Engineer",
        semantic_match=sem,
        sentiment=sent,
        prosody=pros,
        claim_verification=claim,
    )

    ranked_items = [
        {
            "candidate_id": "cand-001",
            "contact_info": {"name": "Sarah Chen"},
            "hybrid_evaluation": hybrid_res.model_dump(),
            "multimodal_analysis": pros.model_dump(),
        }
    ]

    # Test Shortlist CSV
    shortlist_csv = reporting_exporter.export_shortlist_csv(ranked_items)
    reader = csv.reader(io.StringIO(shortlist_csv))
    rows = list(reader)
    assert len(rows) == 2  # Header + 1 candidate row
    assert rows[0][0] == "Rank"
    assert rows[1][1] == "cand-001"

    # Test Shortlist JSON
    shortlist_json = reporting_exporter.export_shortlist_json(ranked_items)
    parsed_json = json.loads(shortlist_json)
    assert len(parsed_json) == 1
    assert parsed_json[0]["candidate_id"] == "cand-001"

    # Test Evaluation Breakdown CSV
    evaluations = [
        {
            "candidate_id": "cand-001",
            "job_id": "jd-ai-001",
            "overall_score": hybrid_res.overall_score,
            "components": hybrid_res.components,
            "recommendation": hybrid_res.recommendation,
            "is_advisory_only": True,
            "recruiter_executive_summary": hybrid_res.recruiter_executive_summary,
        }
    ]
    eval_csv = reporting_exporter.export_evaluation_breakdown_csv(evaluations)
    assert "Overall Score" in eval_csv
    assert "cand-001" in eval_csv

    # Test Fairness Audit Export
    scores = [78.5, 82.0, 91.0, 68.0, 74.0, 88.0, 79.0, 85.0]
    audit_report = fairness_auditor.audit_batch_distribution(scores)

    audit_csv = reporting_exporter.export_fairness_audit_csv(audit_report)
    assert "Fairness & Calibration Metric" in audit_csv
    assert "Sample Size (Candidates)" in audit_csv

    audit_json = reporting_exporter.export_fairness_audit_json(audit_report)
    audit_dict = json.loads(audit_json)
    assert audit_dict["sample_size"] == 8
    assert audit_dict["advisory_compliance_passed"] is True
