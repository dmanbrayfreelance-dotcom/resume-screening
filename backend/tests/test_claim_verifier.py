import pytest
from backend.app.services.multimodal.claim_verifier import (
    claim_verifier,
    ClaimVerificationResult,
)


def test_claim_verifier_clean_alignment():
    """Verify aligned competencies between written resume and spoken transcript."""
    resume_text = (
        "SARAH CHEN\n"
        "AI Engineer with 5 years of experience.\n"
        "SKILLS: Python, PyTorch, FastAPI, Whisper, MongoDB, Docker\n"
        "EXPERIENCE: Senior AI Engineer at NeuralScale (2021 - Present)\n"
    )

    transcript = (
        "Hello everyone, over the last five years I've specialized in building multimodal AI systems. "
        "At NeuralScale, I focused heavily on PyTorch, Whisper speech-to-text, and deployed services with FastAPI."
    )

    res: ClaimVerificationResult = claim_verifier.verify_claims(
        resume_text=resume_text,
        video_transcript=transcript,
    )

    assert "Python" in res.aligned or "PyTorch" in res.aligned
    assert "Whisper" in res.aligned
    assert "FastAPI" in res.aligned
    assert len(res.potential_discrepancy) == 0
    assert res.credibility_score >= 85.0


def test_claim_verifier_detects_tenure_inflation():
    """Verify flagging when candidate verbally claims tenure significantly exceeding resume."""
    resume_text = (
        "ALEX RIVERA\n"
        "Software Engineer with 2 years of experience.\n"
        "EXPERIENCE: Junior Web Developer at Hudson Digital Labs (2022 - 2024)\n"
        "SKILLS: React, TypeScript, Python\n"
    )

    transcript = (
        "Hi, I bring over 7 years of deep professional experience building large-scale platforms."
    )

    res = claim_verifier.verify_claims(
        resume_text=resume_text,
        video_transcript=transcript,
    )

    assert len(res.potential_discrepancy) >= 1
    tenure_disc = next(
        (d for d in res.potential_discrepancy if d.category == "experience_tenure"), None
    )
    assert tenure_disc is not None
    assert tenure_disc.severity == "high"
    assert "7.0 years" in tenure_disc.claim_in_video
    assert res.credibility_score < 75.0
    assert any("Clarify experience timeline" in note for note in res.recruiter_notes)


def test_claim_verifier_detects_unbacked_seniority():
    """Verify flagging when candidate verbally claims executive/leadership title absent on resume."""
    resume_text = (
        "JORDAN SMITH\n"
        "Software Engineer (2021 - Present)\n"
        "SKILLS: Java, Spring Boot, SQL\n"
    )

    transcript = (
        "In my last position, I served as the Chief Technology Officer leading all architectural decisions."
    )

    res = claim_verifier.verify_claims(
        resume_text=resume_text,
        video_transcript=transcript,
    )

    role_disc = next(
        (d for d in res.potential_discrepancy if d.category == "role_seniority"), None
    )
    assert role_disc is not None
    assert "Cto" in role_disc.claim_in_video or "Chief Technology Officer" in role_disc.claim_in_video
    assert role_disc.severity == "medium"
