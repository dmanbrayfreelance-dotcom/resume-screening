import pytest
import uuid
from backend.app.core.config import settings
from backend.app.core.database import (
    COLLECTION_CANDIDATES,
    COLLECTION_JOBS,
    db_manager,
    get_collection,
    is_fallback_active,
)
from backend.app.models.candidate import Candidate, ContactInfo, MultimodalAnalysis
from backend.app.models.job_profile import JobProfile


def test_settings_configuration():
    """Verify all required environment variables and model configs are parsed."""
    assert settings.PROJECT_NAME == "Multimodal Resume Intelligence & Screening Studio"
    assert settings.MONGODB_URI is not None
    assert settings.MONGODB_DB_NAME == "multimodal_resume_intel"
    assert settings.ENABLE_LOCAL_FALLBACK_STORE is True
    assert settings.WHISPER_MODEL_SIZE == "base"
    assert settings.EMBEDDING_MODEL_NAME == "sentence-transformers/all-MiniLM-L6-v2"
    assert settings.SENTIMENT_MODEL_NAME == "nlptown/bert-base-multilingual-uncased-sentiment"


@pytest.mark.asyncio
async def test_database_fallback_operations():
    """Verify local fallback storage handles CRUD operations gracefully."""
    await db_manager.connect_to_mongo()
    assert is_fallback_active() is True

    jobs_col = get_collection(COLLECTION_JOBS)
    test_job_id = f"test-job-{uuid.uuid4()}"

    # Insert test document
    insert_res = await jobs_col.insert_one({
        "job_id": test_job_id,
        "title": "Test AI Specialist",
        "department": "R&D",
        "status": "open",
    })
    assert insert_res.inserted_id is not None

    # Find document
    doc = await jobs_col.find_one({"job_id": test_job_id})
    assert doc is not None
    assert doc["title"] == "Test AI Specialist"

    # Update document
    up_res = await jobs_col.update_one(
        {"job_id": test_job_id},
        {"$set": {"status": "filled"}}
    )
    assert up_res.modified_count == 1

    updated_doc = await jobs_col.find_one({"job_id": test_job_id})
    assert updated_doc["status"] == "filled"

    # Count documents
    count = await jobs_col.count_documents({"job_id": test_job_id})
    assert count == 1

    # Cleanup
    del_res = await jobs_col.delete_one({"job_id": test_job_id})
    assert del_res.deleted_count == 1
    await db_manager.close_mongo_connection()


def test_job_profile_schema_validation():
    """Verify JobProfile Pydantic schema validation."""
    job = JobProfile(
        title="Multimodal NLP Researcher",
        description="Build cutting edge evaluation systems",
        required_skills=["Python", "FastAPI", "Whisper"],
    )
    assert job.title == "Multimodal NLP Researcher"
    assert job.job_id is not None
    assert "Whisper" in job.required_skills
    assert job.scoring_weights.skill_match == 0.35


def test_candidate_schema_validation():
    """Verify Candidate schema with multimodal analysis components."""
    candidate = Candidate(
        contact_info=ContactInfo(
            name="Jane Doe",
            email="jane.doe@example.com",
            location="Austin, TX",
        ),
        skills=["Python", "PyTorch", "Whisper"],
        multimodal_analysis=MultimodalAnalysis(
            duration_seconds=42.0,
            speaking_pace="optimal",
            words_per_minute=135.0,
            sentiment_label="POSITIVE",
            sentiment_score=0.92,
            confidence_score=90.0,
        ),
    )
    assert candidate.contact_info.name == "Jane Doe"
    assert candidate.candidate_id is not None
    assert candidate.multimodal_analysis.speaking_pace == "optimal"
    assert candidate.fairness_metadata.anonymized_view_enabled is True
