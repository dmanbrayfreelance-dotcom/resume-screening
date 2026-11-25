import io
from pathlib import Path
import pytest
from backend.app.services.ingestion.resume_parser import resume_parser
from backend.app.services.ingestion.video_transcriber import video_transcriber
from backend.app.services.nlp.preprocessor import nlp_preprocessor
from backend.app.services.nlp.skill_extractor import skill_extractor

SAMPLE_RESUME_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "sample_resumes"
    / "sarah_chen_ai_engineer.txt"
)
SAMPLE_VIDEO_DIR = Path(__file__).resolve().parents[2] / "data" / "sample_videos"


def test_resume_parser_text_and_pii_scrubbing():
    """Verify resume text parsing, section segmentation, and PII anonymization."""
    assert SAMPLE_RESUME_PATH.exists(), f"Missing fixture: {SAMPLE_RESUME_PATH}"

    parsed = resume_parser.parse(SAMPLE_RESUME_PATH)

    # Verify contact info extraction
    assert parsed.contact_info.name == "SARAH CHEN"
    assert parsed.contact_info.email == "sarah.chen@example.com"
    assert parsed.contact_info.phone is not None
    assert "San Francisco" in (parsed.contact_info.location or "")
    assert "github.com" in (parsed.contact_info.github_url or "")

    # Verify section segmentation
    assert len(parsed.sections.summary) > 20
    assert len(parsed.sections.skills) > 20
    assert len(parsed.sections.experience_projects) > 20
    assert len(parsed.sections.education) > 10

    # Verify PII scrubbing / anonymization
    anonymized = parsed.anonymized_text
    assert anonymized is not None
    assert "sarah.chen@example.com" not in anonymized
    assert "[EMAIL_REDACTED]" in anonymized
    assert "SARAH CHEN" not in anonymized
    assert "[CANDIDATE_NAME]" in anonymized


def test_resume_parser_docx_fallback():
    """Test DOCX parser using python-docx byte stream generation."""
    import docx

    doc = docx.Document()
    doc.add_heading("Jane Developer", 0)
    doc.add_paragraph("Email: jane.dev@example.com | Phone: 555-123-4567")
    doc.add_heading("TECHNICAL SKILLS", level=1)
    doc.add_paragraph("Python, React, TypeScript, Docker, AWS")
    doc.add_heading("WORK EXPERIENCE", level=1)
    doc.add_paragraph("Full-Stack Engineer at TechCorp from 2021 to Present")

    bio = io.BytesIO()
    doc.save(bio)
    docx_bytes = bio.getvalue()

    parsed = resume_parser.parse(docx_bytes, filename="jane_resume.docx")
    assert parsed.file_type == "docx"
    assert parsed.contact_info.email == "jane.dev@example.com"
    assert "Python" in parsed.raw_text
    assert "[EMAIL_REDACTED]" in parsed.anonymized_text


def test_video_transcriber_fixture_fallback():
    """Verify video transcription with deterministic fallback on test fixtures."""
    sample_mp4 = SAMPLE_VIDEO_DIR / "sarah_chen_interview_sample.mp4"
    assert sample_mp4.exists(), f"Sample mp4 missing: {sample_mp4}"

    result = video_transcriber.transcribe(
        sample_mp4, candidate_id="cand-001", force_offline_fallback=True
    )

    assert result.transcription_source == "fixture_manifest"
    assert "multimodal systems" in result.transcript
    assert result.duration_seconds == 45.0
    assert result.speaking_pace == "optimal"
    assert result.words_per_minute > 100
    assert result.word_count > 20


def test_video_transcriber_synthetic_fallback():
    """Verify synthetic fallback for non-fixture media paths."""
    dummy_path = SAMPLE_VIDEO_DIR / "non_existent_candidate.mp4"
    result = video_transcriber.transcribe(dummy_path, force_offline_fallback=True)

    assert result.transcription_source == "synthetic_fallback"
    assert result.duration_seconds > 0
    assert len(result.transcript) > 10
    assert result.speaking_pace in ["slow", "optimal", "fast"]


def test_nlp_preprocessor_protected_tech_terms():
    """Verify technical term protection, stopword removal, and normalization."""
    input_text = "I have built applications using C++, .NET, Node.js, Next.js, and CI/CD pipelines in an AI/ML environment."
    processed = nlp_preprocessor.preprocess(input_text)

    # Check preserved tech terms
    assert "c++" in processed.tokens
    assert ".net" in processed.tokens
    assert "node.js" in processed.tokens
    assert "next.js" in processed.tokens
    assert "ci/cd" in processed.tokens
    assert "ai/ml" in processed.tokens

    # Verify stopwords like 'i', 'have', 'an', 'in' are filtered
    assert "have" not in processed.filtered_tokens
    assert "an" not in processed.filtered_tokens

    # Verify protected tech terms survived filtering and lemmatization intact
    assert "c++" in processed.lemmatized_tokens
    assert ".net" in processed.lemmatized_tokens
    assert "ci/cd" in processed.lemmatized_tokens


def test_skill_extractor_taxonomy_and_aliases():
    """Verify skill taxonomy extraction, aliases mapping, and experience/degree detection."""
    text = (
        "Senior Developer with 5+ years of experience in Python, PyTorch, ReactJS, K8s, and PostgreSQL. "
        "Holds a Master's Degree in Computer Science."
    )
    res = skill_extractor.extract_skills(text)

    # Check canonical normalization (ReactJS -> React, K8s -> Kubernetes, etc.)
    assert "Python" in res.all_skills
    assert "PyTorch" in res.all_skills
    assert "React" in res.all_skills
    assert "Kubernetes" in res.all_skills
    assert "PostgreSQL" in res.all_skills

    # Check categorizations
    assert "Python" in res.skills_by_category["languages"]
    assert "React" in res.skills_by_category["frameworks"]
    assert "Kubernetes" in res.skills_by_category["cloud_devops"]
    assert "PostgreSQL" in res.skills_by_category["databases"]

    # Check experience & education signals
    assert res.experience_years_detected == 5.0
    assert "Master's Degree" in res.education_degrees_detected


def test_skill_extractor_matching_logic():
    """Verify candidate vs JD criteria matching calculation."""
    candidate_skills = ["Python", "FastAPI", "React", "Docker", "MongoDB"]
    required_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    preferred_skills = ["MongoDB", "Kubernetes"]

    report = skill_extractor.match_skills(candidate_skills, required_skills, preferred_skills)

    assert "Python" in report.matched_required
    assert "FastAPI" in report.matched_required
    assert "Docker" in report.matched_required
    assert "PostgreSQL" in report.missing_required
    assert "MongoDB" in report.matched_preferred

    assert report.required_match_ratio == 0.75  # 3 out of 4 required
    assert report.preferred_match_ratio == 0.5   # 1 out of 2 preferred
    assert 60.0 <= report.overall_skill_score <= 85.0
