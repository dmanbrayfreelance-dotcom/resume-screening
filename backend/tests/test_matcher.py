import pytest
import numpy as np
from backend.app.services.nlp.matcher import (
    SemanticEmbeddingEngine,
    semantic_matcher,
    MatchEvaluationResult,
)


def test_embedding_engine_properties():
    """Verify embedding dimensions, determinism, and cosine similarity."""
    engine = SemanticEmbeddingEngine()
    text1 = "FastAPI backend with PyTorch machine learning models"
    text2 = "FastAPI backend with PyTorch machine learning models"
    text3 = "Frontend UI design in Figma and Tailwind CSS"

    emb1 = engine.embed_text(text1)
    emb2 = engine.embed_text(text2)
    emb3 = engine.embed_text(text3)

    assert emb1.shape == (384,)
    assert emb2.shape == (384,)
    # Embedding must be deterministic
    assert np.allclose(emb1, emb2, atol=1e-5)

    # Identical texts should have cosine similarity near 1.0
    sim_identical = engine.cosine_similarity(emb1, emb2)
    assert 0.99 <= sim_identical <= 1.0

    # Dissimilar texts should have lower similarity
    sim_diff = engine.cosine_similarity(emb1, emb3)
    assert sim_diff < sim_identical


def test_matcher_section_weighted_evaluation():
    """Verify section-weighted similarity calculation and skill gap reporting."""
    candidate_sections = {
        "skills": "Python, FastAPI, PyTorch, Whisper, MongoDB, Docker",
        "experience_projects": "Senior AI Engineer designing multimodal speech and NLP pipelines.",
        "education": "Master of Science in Computer Science, University of Washington",
        "raw_text": "Experienced Python and PyTorch engineer deploying Whisper models on FastAPI.",
    }
    candidate_skills = ["Python", "FastAPI", "PyTorch", "Whisper", "MongoDB", "Docker"]

    jd_data = {
        "title": "Senior Multimodal AI Engineer",
        "education_level": "Master's Degree in Computer Science or related",
        "description": "Leading research and productionization of multimodal speech and NLP pipelines.",
        "responsibilities": ["Deploy Whisper models using FastAPI", "Train PyTorch neural networks"],
        "required_skills": ["Python", "FastAPI", "PyTorch", "Whisper", "Kubernetes"],
        "preferred_skills": ["Docker", "MongoDB", "ONNX Runtime"],
        "scoring_weights": {
            "skill_match": 0.40,
            "experience_match": 0.30,
            "education_match": 0.15,
            "semantic_fit": 0.15,
        },
    }

    result: MatchEvaluationResult = semantic_matcher.evaluate_match(
        candidate_sections=candidate_sections,
        candidate_skills=candidate_skills,
        jd_data=jd_data,
    )

    assert 60.0 <= result.overall_fit_score <= 100.0
    assert "skills" in result.section_scores
    assert "experience" in result.section_scores

    # Skill gap report verification
    gap = result.skill_gap
    assert "Whisper" in gap.matched_skills
    assert "Python" in gap.matched_skills
    assert "Kubernetes" in gap.missing_required_skills
    assert "ONNX Runtime" in gap.missing_preferred_skills
    assert gap.coverage_pct == 80.0  # 4 out of 5 required

    # Recommendations should suggest bridging missing Kubernetes requirement
    assert len(gap.recommendations) > 0
    assert any("Kubernetes" in r for r in gap.recommendations)


def test_matcher_full_coverage_scenario():
    """Verify behavior when candidate possesses 100% of required skills."""
    candidate_sections = {
        "skills": "Python, FastAPI, Docker",
        "experience_projects": "Built REST APIs with Python and Docker.",
        "education": "BS in Computer Science",
    }
    candidate_skills = ["Python", "FastAPI", "Docker"]

    jd_data = {
        "title": "Junior Python Developer",
        "description": "Develop web services in Python and FastAPI.",
        "responsibilities": ["Maintain Dockerized endpoints"],
        "required_skills": ["Python", "FastAPI", "Docker"],
        "preferred_skills": [],
    }

    result = semantic_matcher.evaluate_match(
        candidate_sections=candidate_sections,
        candidate_skills=candidate_skills,
        jd_data=jd_data,
    )

    assert result.skill_gap.coverage_pct == 100.0
    assert len(result.skill_gap.missing_required_skills) == 0
    assert any("full technical skill coverage" in r.lower() for r in result.skill_gap.recommendations)
