from fastapi import APIRouter
from backend.app.api.routes import analytics, candidates, health, jobs

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
