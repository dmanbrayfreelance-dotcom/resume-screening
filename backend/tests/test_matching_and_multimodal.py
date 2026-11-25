import json
from pathlib import Path
import pytest
from backend.app.services.nlp.matcher import semantic_matcher, SemanticEmbeddingEngine
from backend.app.services.multimodal.sentiment_analyzer import sentiment_analyzer
from backend.app.services.multimodal.prosody_vision import prosody_vision
from backend.app.services.multimodal.claim_verifier import claim_verifier

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
JD_PATH = DATA_DIR / "sample_jds" / "ai_engineer_jd.json"
RESUME_PATH = DATA_DIR / "sample_resumes" / "sarah_chen_ai_engineer.txt"
WAV_PATH = DATA_DIR / "sample_videos" / "sarah_chen_interview_sample.wav"


def test_semantic_matcher_and_skill_gap_explainability():
    """Verify section-weighted match scoring, embedding fallback, and recommendations."""
    with open(JD_PATH, "r", encoding="utf-8") as f:
        jd_data = json.load(f)

    with open(RESUME_PATH, "r", encoding="utf-8") as f:
        resume_text = f.read()

    candidate_sections = {
        "raw_text": resume_text,
        "skills": "Python, PyTorch, FastAPI, Transformers, Whisper, LangChain, MongoDB",
        "experience_projects": "Senior AI Engineer deploying Whisper ASR and transformer pipelines with FastAPI microservices.",
        "education": "Master of Science in Computer Science, UC Berkeley Bachelor in Data Science",
    }
    candidate_skills = ["Python", "PyTorch", "FastAPI", "Whisper", "MongoDB", "Transformers"]

    result = semantic_matcher.evaluate_match(
        candidate_sections=candidate_sections,
        candidate_skills=candidate_skills,
        jd_data=jd_data,
    )

    # Check overall fit score
    assert 60.0 <= result.overall_fit_score <= 100.0
    assert "skills" in result.section_scores
    assert "experience" in result.section_scores
    assert "education" in result.section_scores
    assert "semantic_fit" in result.section_scores

    # Check skill-gap explainability
    assert "Whisper" in result.skill_gap.matched_skills
    assert "Python" in result.skill_gap.matched_skills
    assert result.skill_gap.coverage_pct >= 50.0

    # Check that recommendations are generated for any missing skills
    if result.skill_gap.missing_required_skills:
        assert len(result.skill_gap.recommendations) > 0

    # Check embedding engine
    engine = SemanticEmbeddingEngine()
    emb = engine.embed_text("FastAPI machine learning microservice")
    assert emb.shape == (384,)
    sim = engine.cosine_similarity(emb, emb)
    assert 0.99 <= sim <= 1.0


def test_sentiment_analyzer_polarity():
    """Verify positive, neutral, and negative sentiment classification."""
    pos_transcript = (
        "I am very excited and proud to have successfully optimized and scaled our AI models. "
        "I loved collaborating with the engineering team to solve challenging problems."
    )
    res_pos = sentiment_analyzer.analyze(pos_transcript)
    assert res_pos.label == "POSITIVE"
    assert res_pos.polarity_score > 0.55
    assert res_pos.positive_prob > res_pos.negative_prob

    neg_transcript = (
        "We struggled and failed repeatedly. The team faced terrible conflicts and was frustrated "
        "with the broken and problematic legacy code."
    )
    res_neg = sentiment_analyzer.analyze(neg_transcript)
    assert res_neg.label == "NEGATIVE"
    assert res_neg.polarity_score < 0.45

    neutral_transcript = (
        "The project started in July. We held daily standup meetings at 9 AM and recorded our tasks."
    )
    res_neu = sentiment_analyzer.analyze(neutral_transcript)
    assert res_neu.label in ["NEUTRAL", "POSITIVE"]


def test_prosody_and_vision_analyzer():
    """Verify speech pace, filler word ratio, acoustic energy, and graceful degradation."""
    transcript = (
        "Um, basically, I have five years of experience. We, like, deployed Whisper models "
        "and, you know, optimized latency for production."
    )
    result = prosody_vision.analyze(
        transcript_text=transcript,
        duration_seconds=15.0,
        audio_path=WAV_PATH if WAV_PATH.exists() else None,
    )

    assert result.words_per_minute > 50.0
    assert result.filler_word_ratio > 0.05
    assert len(result.filler_words_detected) >= 2
    assert any("filler-word" in a.lower() for a in result.flagged_anomalies)

    # Verify graceful degradation on text-only input
    degraded = prosody_vision.analyze(
        transcript_text="Smooth delivery with no filler words and steady articulation.",
        duration_seconds=20.0,
        audio_path=None,
        video_path=None,
    )
    assert degraded.analysis_mode == "text_prosody_degraded"
    assert degraded.overall_presentation_score > 70.0
    assert degraded.filler_word_ratio == 0.0


def test_multimodal_claim_verifier_alignment_and_discrepancy():
    """Verify alignment of shared claims and flagging of discrepancies in tenure and title."""
    resume = (
        "John Doe\n"
        "Software Engineer with 3 years of experience.\n"
        "SKILLS: Python, FastAPI, Docker, PostgreSQL\n"
        "EXPERIENCE: Software Engineer at DataCorp (2021 - Present)\n"
    )

    # 1. Aligned scenario
    video_aligned = (
        "Hello, over the past three years as a software engineer, I have built REST APIs with Python, "
        "FastAPI, and Docker, and also learned Kubernetes recently."
    )
    res_aligned = claim_verifier.verify_claims(resume_text=resume, video_transcript=video_aligned)

    assert "Python" in res_aligned.aligned
    assert "FastAPI" in res_aligned.aligned
    assert "Kubernetes" in res_aligned.mentioned_only_in_video
    assert "PostgreSQL" in res_aligned.mentioned_only_in_resume
    assert len(res_aligned.potential_discrepancy) == 0
    assert res_aligned.credibility_score >= 80.0

    # 2. Discrepancy scenario: inflated experience and unbacked executive title
    video_discrepant = (
        "I served as the Principal Director of engineering with over 8 years of experience "
        "managing enterprise distributed systems."
    )
    res_discrepant = claim_verifier.verify_claims(resume_text=resume, video_transcript=video_discrepant)

    assert len(res_discrepant.potential_discrepancy) >= 1
    tenure_disc = next(
        (d for d in res_discrepant.potential_discrepancy if d.category == "experience_tenure"), None
    )
    assert tenure_disc is not None
    assert tenure_disc.severity in ["medium", "high"]
    assert res_discrepant.credibility_score < res_aligned.credibility_score
