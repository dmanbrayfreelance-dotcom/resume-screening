import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Response, status

from backend.app.core.database import (
    COLLECTION_CANDIDATES,
    COLLECTION_JOBS,
    get_collection,
)
from backend.app.services.ranking.fairness_audit import fairness_auditor
from backend.app.services.reporting.exporter import reporting_exporter

router = APIRouter()


@router.get("/leaderboard/{job_id}")
async def get_job_leaderboard(job_id: str):
    """
    Returns ranked candidate leaderboard for a target Job Description
    sorted by composite hybrid fit score.
    """
    jobs_col = get_collection(COLLECTION_JOBS)
    job_doc = await jobs_col.find_one({"job_id": job_id})
    if not job_doc:
        raise HTTPException(status_code=404, detail=f"Job Profile '{job_id}' not found")

    candidates_col = get_collection(COLLECTION_CANDIDATES)
    cursor = candidates_col.find({"evaluations.job_id": job_id})
    candidates_list = await cursor.to_list()

    leaderboard = []
    for cand in candidates_list:
        contact = cand.get("contact_info", {})
        multimodal = cand.get("multimodal_analysis", {})

        target_eval = None
        for ev in cand.get("evaluations", []):
            if ev.get("job_id") == job_id:
                target_eval = ev
                break

        if not target_eval:
            continue

        score = float(target_eval.get("overall_fit_score", 0.0))
        skill_gap = target_eval.get("skill_gap", {})
        claims = target_eval.get("claim_verification", {})

        leaderboard.append({
            "candidate_id": cand.get("candidate_id"),
            "candidate_name": contact.get("name", "Candidate"),
            "email": contact.get("email"),
            "overall_fit_score": score,
            "recommendation": target_eval.get("recommendation", "Review"),
            "is_advisory_only": True,
            "skill_coverage_pct": skill_gap.get("coverage_pct", 0.0),
            "matched_skills": skill_gap.get("matched_skills", []),
            "missing_required_skills": skill_gap.get("missing_required_skills", []),
            "speaking_pace": multimodal.get("speaking_pace", "optimal"),
            "sentiment_label": multimodal.get("sentiment_label", "POSITIVE"),
            "credibility_score": claims.get("credibility_score", 90.0),
            "discrepancies_count": len(claims.get("potential_discrepancy", [])),
            "recruiter_executive_summary": target_eval.get("recruiter_executive_summary", ""),
        })

    # Sort descending by overall score
    leaderboard.sort(key=lambda x: x["overall_fit_score"], reverse=True)

    # Attach rank
    for rank, item in enumerate(leaderboard, start=1):
        item["rank"] = rank

    return {
        "job_id": job_id,
        "job_title": job_doc.get("title", ""),
        "total_candidates": len(leaderboard),
        "leaderboard": leaderboard,
    }


@router.get("/fairness/{job_id}")
async def get_fairness_audit(job_id: str):
    """
    Computes statistical score distribution, spread, threshold-sensitivity rates,
    and calibration drift metrics across all candidates evaluated for the JD.
    """
    jobs_col = get_collection(COLLECTION_JOBS)
    job_doc = await jobs_col.find_one({"job_id": job_id})
    if not job_doc:
        raise HTTPException(status_code=404, detail=f"Job Profile '{job_id}' not found")

    candidates_col = get_collection(COLLECTION_CANDIDATES)
    cursor = candidates_col.find({"evaluations.job_id": job_id})
    candidates_list = await cursor.to_list()

    scores = []
    for cand in candidates_list:
        for ev in cand.get("evaluations", []):
            if ev.get("job_id") == job_id:
                scores.append(float(ev.get("overall_fit_score", 0.0)))

    audit_report = fairness_auditor.audit_batch_distribution(scores)

    return {
        "job_id": job_id,
        "job_title": job_doc.get("title", ""),
        "audit_report": audit_report.model_dump(),
    }


@router.get("/export/{job_id}")
async def export_job_report(
    job_id: str,
    format: str = Query("json", pattern="^(json|csv)$"),
):
    """
    Exports ranked candidate shortlist and evaluation metrics as JSON or CSV download.
    """
    jobs_col = get_collection(COLLECTION_JOBS)
    job_doc = await jobs_col.find_one({"job_id": job_id})
    if not job_doc:
        raise HTTPException(status_code=404, detail=f"Job Profile '{job_id}' not found")

    candidates_col = get_collection(COLLECTION_CANDIDATES)
    cursor = candidates_col.find({"evaluations.job_id": job_id})
    candidates_list = await cursor.to_list()

    ranked_items = []
    for cand in candidates_list:
        for ev in cand.get("evaluations", []):
            if ev.get("job_id") == job_id:
                ranked_items.append({
                    "candidate_id": cand.get("candidate_id"),
                    "contact_info": cand.get("contact_info", {}),
                    "hybrid_evaluation": ev,
                    "multimodal_analysis": cand.get("multimodal_analysis", {}),
                    "overall_fit_score": ev.get("overall_fit_score", 0.0),
                })

    ranked_items.sort(key=lambda x: x.get("overall_fit_score", 0.0), reverse=True)

    if format == "csv":
        csv_content = reporting_exporter.export_shortlist_csv(ranked_items)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=shortlist_{job_id}.csv"},
        )
    else:
        json_content = reporting_exporter.export_shortlist_json(ranked_items)
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=shortlist_{job_id}.json"},
        )
