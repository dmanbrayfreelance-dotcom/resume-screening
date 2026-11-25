from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from backend.app.core.database import COLLECTION_JOBS, get_collection
from backend.app.models.job_profile import (
    JobProfile,
    JobProfileCreate,
    JobProfileUpdate,
    ScoringWeights,
)

router = APIRouter()


@router.get("/", response_model=List[JobProfile])
async def list_jobs(status_filter: Optional[str] = None):
    """Retrieve all job profiles."""
    col = get_collection(COLLECTION_JOBS)
    query = {"status": status_filter} if status_filter else {}
    cursor = col.find(query)
    jobs = await cursor.to_list()
    return jobs


@router.post("/", response_model=JobProfile, status_code=status.HTTP_201_CREATED)
async def create_job(job_in: JobProfileCreate):
    """Create a new job screening profile with custom section/modality weights."""
    col = get_collection(COLLECTION_JOBS)
    job = JobProfile(**job_in.model_dump())
    await col.insert_one(job.model_dump())
    return job


@router.get("/{job_id}", response_model=JobProfile)
async def get_job(job_id: str):
    """Fetch specific job profile by job_id."""
    col = get_collection(COLLECTION_JOBS)
    doc = await col.find_one({"job_id": job_id})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Job profile '{job_id}' not found")
    return doc


@router.patch("/{job_id}/weights", response_model=JobProfile)
async def update_job_weights(job_id: str, weights: ScoringWeights):
    """Update section and modality scoring weights for candidate ranking."""
    col = get_collection(COLLECTION_JOBS)
    existing = await col.find_one({"job_id": job_id})
    if not existing:
        raise HTTPException(status_code=404, detail=f"Job profile '{job_id}' not found")

    weights_dict = weights.model_dump()
    updated_at = datetime.now(timezone.utc).isoformat()

    await col.update_one(
        {"job_id": job_id},
        {"$set": {"scoring_weights": weights_dict, "updated_at": updated_at}},
    )

    updated_doc = await col.find_one({"job_id": job_id})
    return updated_doc


@router.put("/{job_id}", response_model=JobProfile)
async def update_job(job_id: str, job_update: JobProfileUpdate):
    """Update general job profile fields."""
    col = get_collection(COLLECTION_JOBS)
    update_data = {k: v for k, v in job_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await col.update_one({"job_id": job_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"Job profile '{job_id}' not found")

    updated_doc = await col.find_one({"job_id": job_id})
    return updated_doc


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str):
    """Remove a job profile."""
    col = get_collection(COLLECTION_JOBS)
    result = await col.delete_one({"job_id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Job profile '{job_id}' not found")
    return None
