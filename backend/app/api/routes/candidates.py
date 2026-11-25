import logging
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.app.core.database import (
    COLLECTION_CANDIDATES,
    COLLECTION_EVALUATIONS,
    COLLECTION_JOBS,
    get_collection,
)
from backend.app.models.candidate import Candidate
from backend.app.services.ingestion.resume_parser import resume_parser
from backend.app.services.ingestion.video_transcriber import video_transcriber
from backend.app.services.nlp.matcher import semantic_matcher
from backend.app.services.nlp.skill_extractor import skill_extractor
from backend.app.services.multimodal.claim_verifier import claim_verifier
from backend.app.services.multimodal.prosody_vision import prosody_vision
from backend.app.services.multimodal.sentiment_analyzer import sentiment_analyzer
from backend.app.services.ranking.fairness_audit import fairness_auditor
from backend.app.services.ranking.hybrid_scorer import hybrid_scorer

logger = logging.getLogger("app.api.routes.candidates")
router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_candidates(job_id: Optional[str] = None, status_filter: Optional[str] = None):
    """Retrieve all candidate profiles with optional job_id or status filters."""
    col = get_collection(COLLECTION_CANDIDATES)
    query: Dict[str, Any] = {}
    if status_filter:
        query["status"] = status_filter
    if job_id:
        query["evaluations.job_id"] = job_id

    cursor = col.find(query)
    candidates = await cursor.to_list()
    return candidates


@router.get("/{candidate_id}", response_model=Dict[str, Any])
async def get_candidate(candidate_id: str):
    """Retrieve candidate profile by ID."""
    col = get_collection(COLLECTION_CANDIDATES)
    doc = await col.find_one({"candidate_id": candidate_id})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found")
    return doc


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(candidate_id: str):
    """Delete candidate profile and associated evaluations."""
    col_c = get_collection(COLLECTION_CANDIDATES)
    col_e = get_collection(COLLECTION_EVALUATIONS)

    res = await col_c.delete_one({"candidate_id": candidate_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found")

    await col_e.delete_one({"candidate_id": candidate_id})
    return None


@router.post("/evaluate", status_code=status.HTTP_201_CREATED)
async def evaluate_candidate(
    job_id: str = Form(..., description="Target Job Profile ID"),
    resume_file: UploadFile = File(..., description="Candidate resume PDF/DOCX/TXT"),
    video_file: Optional[UploadFile] = File(None, description="Optional MP4/WEBM video resume"),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
):
    """
    End-to-end multimodal screening endpoint:
    Parses resume, extracts skills, processes video interview (transcription, prosody, sentiment),
    verifies cross-modal claims, computes hybrid scoring against JD criteria, and persists evaluation.
    """
    # 1. Verify Job Profile
    jobs_col = get_collection(COLLECTION_JOBS)
    job_doc = await jobs_col.find_one({"job_id": job_id})
    if not job_doc:
        raise HTTPException(
            status_code=404,
            detail=f"Target Job Profile '{job_id}' does not exist. Please create JD first.",
        )

    # 2. Parse Resume
    resume_bytes = await resume_file.read()
    parsed_resume = resume_parser.parse(resume_bytes, filename=resume_file.filename)

    contact_info = parsed_resume.contact_info.model_dump()
    if name:
        contact_info["name"] = name
    if email:
        contact_info["email"] = email
    if phone:
        contact_info["phone"] = phone
    if location:
        contact_info["location"] = location

    candidate_name = contact_info.get("name") or "Candidate"
    candidate_id = f"cand-{uuid.uuid4().hex[:8]}"

    # 3. Process Video Interview (if provided)
    temp_video_path = None
    transcription_result = None
    sentiment_result = None
    prosody_result = None

    if video_file is not None and video_file.filename:
        suffix = Path(video_file.filename).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await video_file.read())
            temp_video_path = Path(tmp.name)

        try:
            # Transcription (with offline fixture fallback)
            transcription_result = video_transcriber.transcribe(
                temp_video_path, candidate_id=candidate_id
            )
            transcript_text = transcription_result.transcript

            # Sentiment Analysis
            sentiment_result = sentiment_analyzer.analyze(transcript_text)

            # Speech Prosody and Vision Analysis
            prosody_result = prosody_vision.analyze(
                transcript_text=transcript_text,
                duration_seconds=transcription_result.duration_seconds,
                audio_path=transcription_result.audio_wav_path,
                video_path=temp_video_path,
            )
        finally:
            # Cleanup temp file
            if temp_video_path and temp_video_path.exists():
                try:
                    os.remove(temp_video_path)
                except Exception:
                    pass
    else:
        # Default text-only profile
        transcript_text = ""
        sentiment_result = sentiment_analyzer.analyze("")
        prosody_result = prosody_vision.analyze(transcript_text="", duration_seconds=1.0)

    # 4. Extract Skills from written resume and spoken transcript
    resume_skills_extracted = skill_extractor.extract_skills(parsed_resume.raw_text)
    candidate_skills = resume_skills_extracted.all_skills

    # 5. Cross-Modal Claim Verification
    claim_result = claim_verifier.verify_claims(
        resume_text=parsed_resume.raw_text,
        video_transcript=transcript_text,
        known_resume_skills=candidate_skills,
    )

    # 6. Semantic Matching against Job Description
    sections_dict = parsed_resume.sections.model_dump()
    sections_dict["raw_text"] = parsed_resume.raw_text

    semantic_result = semantic_matcher.evaluate_match(
        candidate_sections=sections_dict,
        candidate_skills=candidate_skills,
        jd_data=job_doc,
        scoring_weights=job_doc.get("scoring_weights"),
    )

    # 7. Hybrid Ranking Synthesis
    hybrid_score = hybrid_scorer.score_candidate(
        candidate_name=candidate_name,
        job_title=job_doc.get("title", "Target Role"),
        semantic_match=semantic_result,
        sentiment=sentiment_result,
        prosody=prosody_result,
        claim_verification=claim_result,
        custom_weights=job_doc.get("scoring_weights"),
    )

    # 8. Anonymized Fairness View
    cand_dict = {
        "candidate_id": candidate_id,
        "contact_info": contact_info,
        "summary": parsed_resume.sections.summary,
        "skills": candidate_skills,
        "raw_resume_text": parsed_resume.raw_text,
        "multimodal_analysis": {
            "transcript": transcript_text,
            "speaking_pace": prosody_result.speaking_pace,
            "words_per_minute": prosody_result.words_per_minute,
            "sentiment_label": sentiment_result.label,
            "confidence_score": prosody_result.overall_presentation_score,
        },
    }
    anonymized_view = fairness_auditor.anonymize_for_review(cand_dict)

    # 9. Build Database Document
    now_iso = datetime.now(timezone.utc).isoformat()
    evaluation_record = {
        "evaluation_id": f"eval-{uuid.uuid4().hex[:8]}",
        "job_id": job_id,
        "overall_fit_score": hybrid_score.overall_score,
        "recommendation": hybrid_score.recommendation,
        "is_advisory_only": True,
        "component_breakdown": {k: v.model_dump() for k, v in hybrid_score.components.items()},
        "skill_gap": semantic_result.skill_gap.model_dump(),
        "claim_verification": claim_result.model_dump(),
        "strengths": hybrid_score.strengths,
        "areas_for_probing": hybrid_score.areas_for_probing,
        "recruiter_executive_summary": hybrid_score.recruiter_executive_summary,
        "evaluated_at": now_iso,
    }

    candidate_doc = {
        "candidate_id": candidate_id,
        "contact_info": contact_info,
        "summary": parsed_resume.sections.summary,
        "skills": candidate_skills,
        "sections": sections_dict,
        "multimodal_analysis": {
            "transcript": transcript_text,
            "duration_seconds": transcription_result.duration_seconds if transcription_result else 0.0,
            "words_per_minute": prosody_result.words_per_minute,
            "speaking_pace": prosody_result.speaking_pace,
            "filler_word_ratio": prosody_result.filler_word_ratio,
            "sentiment_label": sentiment_result.label,
            "sentiment_score": sentiment_result.polarity_score,
            "presentation_score": prosody_result.overall_presentation_score,
            "vocal_energy_score": prosody_result.vocal_energy_score,
            "visual_engagement_score": prosody_result.visual_engagement_score,
            "analysis_mode": prosody_result.analysis_mode,
        },
        "evaluations": [evaluation_record],
        "anonymized_view": anonymized_view.model_dump(),
        "status": "screened",
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    candidates_col = get_collection(COLLECTION_CANDIDATES)
    await candidates_col.insert_one(candidate_doc)

    eval_col = get_collection(COLLECTION_EVALUATIONS)
    await eval_col.insert_one({
        "candidate_id": candidate_id,
        **evaluation_record,
    })

    return {
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "job_id": job_id,
        "overall_fit_score": hybrid_score.overall_score,
        "recommendation": hybrid_score.recommendation,
        "is_advisory_only": True,
        "components": {k: v.model_dump() for k, v in hybrid_score.components.items()},
        "skill_gap": semantic_result.skill_gap.model_dump(),
        "claim_verification": claim_result.model_dump(),
        "recruiter_executive_summary": hybrid_score.recruiter_executive_summary,
        "anonymized_view": anonymized_view.model_dump(),
    }


@router.post("/re-rank/{job_id}", response_model=List[Dict[str, Any]])
async def rerank_candidates(job_id: str):
    """
    Re-scores all candidates previously evaluated for a specific Job Description
    using updated section and modality weights, updating the persisted leaderboard.
    """
    jobs_col = get_collection(COLLECTION_JOBS)
    job_doc = await jobs_col.find_one({"job_id": job_id})
    if not job_doc:
        raise HTTPException(status_code=404, detail=f"Job Profile '{job_id}' not found")

    weights = job_doc.get("scoring_weights", {})
    candidates_col = get_collection(COLLECTION_CANDIDATES)

    cursor = candidates_col.find({"evaluations.job_id": job_id})
    candidates_list = await cursor.to_list()

    reranked_results = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for cand in candidates_list:
        candidate_id = cand.get("candidate_id")
        candidate_name = cand.get("contact_info", {}).get("name", "Candidate")

        # Extract stored sections & skills
        sections = cand.get("sections", {})
        skills = cand.get("skills", [])
        multimodal = cand.get("multimodal_analysis", {})

        # Re-evaluate semantic match with updated JD
        semantic_res = semantic_matcher.evaluate_match(
            candidate_sections=sections,
            candidate_skills=skills,
            jd_data=job_doc,
            scoring_weights=weights,
        )

        # Mock sentiment & prosody results from stored multimodal data
        from backend.app.services.multimodal.sentiment_analyzer import SentimentAnalysisResult
        from backend.app.services.multimodal.prosody_vision import ProsodyVisionResult
        from backend.app.services.multimodal.claim_verifier import ClaimVerificationResult

        sent_obj = SentimentAnalysisResult(
            label=multimodal.get("sentiment_label", "POSITIVE"),
            polarity_score=float(multimodal.get("sentiment_score", 0.85)),
            positive_prob=0.85,
            neutral_prob=0.10,
            negative_prob=0.05,
        )
        pros_obj = ProsodyVisionResult(
            speaking_pace=multimodal.get("speaking_pace", "optimal"),
            words_per_minute=float(multimodal.get("words_per_minute", 135.0)),
            filler_word_ratio=float(multimodal.get("filler_word_ratio", 0.02)),
            overall_presentation_score=float(multimodal.get("presentation_score", 88.0)),
        )

        # Get existing claim verification or re-verify
        existing_claims = {}
        for ev in cand.get("evaluations", []):
            if ev.get("job_id") == job_id:
                existing_claims = ev.get("claim_verification", {})
                break

        claim_obj = ClaimVerificationResult(
            credibility_score=float(existing_claims.get("credibility_score", 90.0)),
            aligned=existing_claims.get("aligned", []),
            mentioned_only_in_video=existing_claims.get("mentioned_only_in_video", []),
            mentioned_only_in_resume=existing_claims.get("mentioned_only_in_resume", []),
            potential_discrepancy=existing_claims.get("potential_discrepancy", []),
        )

        # Recompute hybrid score with new weights
        new_hybrid = hybrid_scorer.score_candidate(
            candidate_name=candidate_name,
            job_title=job_doc.get("title", "Target Role"),
            semantic_match=semantic_res,
            sentiment=sent_obj,
            prosody=pros_obj,
            claim_verification=claim_obj,
            custom_weights=weights,
        )

        # Update evaluation in candidate record
        evaluations = cand.get("evaluations", [])
        for ev in evaluations:
            if ev.get("job_id") == job_id:
                ev["overall_fit_score"] = new_hybrid.overall_score
                ev["recommendation"] = new_hybrid.recommendation
                ev["component_breakdown"] = {
                    k: v.model_dump() for k, v in new_hybrid.components.items()
                }
                ev["strengths"] = new_hybrid.strengths
                ev["areas_for_probing"] = new_hybrid.areas_for_probing
                ev["recruiter_executive_summary"] = new_hybrid.recruiter_executive_summary
                ev["updated_at"] = now_iso

        await candidates_col.update_one(
            {"candidate_id": candidate_id},
            {"$set": {"evaluations": evaluations, "updated_at": now_iso}},
        )

        reranked_results.append({
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "overall_fit_score": new_hybrid.overall_score,
            "recommendation": new_hybrid.recommendation,
            "skill_coverage_pct": semantic_res.skill_gap.coverage_pct,
            "recruiter_executive_summary": new_hybrid.recruiter_executive_summary,
        })

    # Sort descending by updated overall score
    reranked_results.sort(key=lambda x: x["overall_fit_score"], reverse=True)
    return reranked_results
