import io
import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import db_manager


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient instance with pre-initialized fallback database."""
    # Ensure local fallback storage is active for testing
    db_manager._activate_fallback()
    with TestClient(app) as test_client:
        yield test_client


def test_api_health_endpoints(client):
    """Verify root /health and /api/health return status, Atlas connectivity, and model modes."""
    # Root /health
    res_root = client.get("/health")
    assert res_root.status_code == 200
    data_root = res_root.json()
    assert data_root["status"] == "healthy"
    assert data_root["mongodb_atlas_connectivity"] in ["fallback", "connected"]
    assert "active_models" in data_root

    # API v1 /api/health
    res_api = client.get("/api/health")
    assert res_api.status_code == 200
    assert res_api.json()["status"] == "healthy"


def test_api_job_lifecycle_and_patch_weights(client):
    """Test creating a JD with custom weights, retrieving it, and patching scoring weights."""
    job_payload = {
        "title": "Senior AI Screening Lead",
        "department": "Talent Intelligence",
        "description": "Architect multimodal candidate screening pipelines using Whisper and FastAPI.",
        "required_skills": ["Python", "FastAPI", "Whisper", "PyTorch", "Docker"],
        "preferred_skills": ["MongoDB", "Kubernetes"],
        "scoring_weights": {
            "skill_match": 0.35,
            "experience_match": 0.25,
            "multimodal_presentation": 0.15,
            "sentiment_engagement": 0.10,
            "claim_credibility": 0.15,
        },
    }

    # 1. Create Job
    create_res = client.post("/api/jobs/", json=job_payload)
    assert create_res.status_code == 201
    created_job = create_res.json()
    job_id = created_job["job_id"]
    assert created_job["title"] == "Senior AI Screening Lead"

    # 2. Get Job
    get_res = client.get(f"/api/jobs/{job_id}")
    assert get_res.status_code == 200
    assert get_res.json()["job_id"] == job_id

    # 3. Patch Weights
    new_weights = {
        "skill_match": 0.50,
        "experience_match": 0.20,
        "multimodal_presentation": 0.10,
        "sentiment_engagement": 0.10,
        "claim_credibility": 0.10,
    }
    patch_res = client.patch(f"/api/jobs/{job_id}/weights", json=new_weights)
    assert patch_res.status_code == 200
    patched_job = patch_res.json()
    assert patched_job["scoring_weights"]["skill_match"] == 0.50


def test_api_candidate_evaluate_and_rerank(client):
    """Test full multipart evaluation endpoint, candidate retrieval, and re-ranking."""
    # 1. Create target job
    job_res = client.post(
        "/api/jobs/",
        json={
            "title": "Full-Stack AI Developer",
            "description": "Build high-throughput FastAPI and React recruitment tools.",
            "required_skills": ["Python", "FastAPI", "React", "TypeScript", "Docker"],
            "preferred_skills": ["MongoDB", "Whisper"],
        },
    )
    assert job_res.status_code == 201
    job_id = job_res.json()["job_id"]

    # 2. Multipart candidate resume upload
    sample_resume_content = (
        "SARAH DEV\n"
        "sarah.dev@example.com | (555) 019-2834 | New York, NY\n"
        "LinkedIn: linkedin.com/in/sarah-dev\n\n"
        "SUMMARY\n"
        "Full-Stack Developer with 4 years building FastAPI services and React interfaces.\n\n"
        "TECHNICAL SKILLS\n"
        "Python, FastAPI, React, TypeScript, Docker, MongoDB\n\n"
        "EXPERIENCE\n"
        "Software Engineer at CloudScale (2020 - Present)\n"
        "- Engineered microservices handling candidate data.\n"
    )

    resume_file = ("resume.txt", io.BytesIO(sample_resume_content.encode("utf-8")), "text/plain")

    form_data = {
        "job_id": job_id,
        "name": "Sarah Dev",
        "email": "sarah.dev@example.com",
    }

    eval_res = client.post(
        "/api/candidates/evaluate",
        data=form_data,
        files={"resume_file": resume_file},
    )
    assert eval_res.status_code == 201
    eval_data = eval_res.json()
    candidate_id = eval_data["candidate_id"]

    assert eval_data["overall_fit_score"] > 60.0
    assert eval_data["is_advisory_only"] is True
    assert "components" in eval_data
    assert "skill_gap" in eval_data
    assert "anonymized_view" in eval_data

    # 3. Retrieve Candidate
    get_cand = client.get(f"/api/candidates/{candidate_id}")
    assert get_cand.status_code == 200
    assert get_cand.json()["candidate_id"] == candidate_id

    # 4. Patch Job weights and re-rank candidates
    client.patch(
        f"/api/jobs/{job_id}/weights",
        json={"skill_match": 0.60, "experience_match": 0.20, "multimodal_presentation": 0.10, "sentiment_engagement": 0.05, "claim_credibility": 0.05},
    )
    rerank_res = client.post(f"/api/candidates/re-rank/{job_id}")
    assert rerank_res.status_code == 200
    reranked_list = rerank_res.json()
    assert len(reranked_list) >= 1
    assert reranked_list[0]["candidate_id"] == candidate_id

    # 5. Analytics Leaderboard
    leaderboard_res = client.get(f"/api/analytics/leaderboard/{job_id}")
    assert leaderboard_res.status_code == 200
    lb_data = leaderboard_res.json()
    assert lb_data["total_candidates"] >= 1
    assert lb_data["leaderboard"][0]["rank"] == 1

    # 6. Analytics Fairness Audit
    fairness_res = client.get(f"/api/analytics/fairness/{job_id}")
    assert fairness_res.status_code == 200
    fairness_data = fairness_res.json()
    assert "audit_report" in fairness_data
    assert fairness_data["audit_report"]["advisory_compliance_passed"] is True

    # 7. Analytics Export CSV
    export_csv_res = client.get(f"/api/analytics/export/{job_id}?format=csv")
    assert export_csv_res.status_code == 200
    assert "text/csv" in export_csv_res.headers.get("content-type", "")
    assert "Candidate ID" in export_csv_res.text

    # 8. Analytics Export JSON
    export_json_res = client.get(f"/api/analytics/export/{job_id}?format=json")
    assert export_json_res.status_code == 200
    assert "application/json" in export_json_res.headers.get("content-type", "")
    parsed_export = export_json_res.json()
    assert len(parsed_export) >= 1

    # 9. Clean up candidate
    del_cand = client.delete(f"/api/candidates/{candidate_id}")
    assert del_cand.status_code == 204
