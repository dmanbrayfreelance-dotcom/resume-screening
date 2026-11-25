from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.core.database import is_fallback_active

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check():
    """Returns application health, Atlas connectivity status, and active model modes."""
    fallback_active = is_fallback_active()
    return {
        "status": "healthy",
        "project_name": settings.PROJECT_NAME,
        "mongodb_atlas_connectivity": "fallback" if fallback_active else "connected",
        "database_mode": "fallback_store (offline)" if fallback_active else "mongodb_atlas (online)",
        "active_models": {
            "whisper_asr": settings.WHISPER_MODEL_SIZE,
            "embedding_engine": settings.EMBEDDING_MODEL_NAME,
            "sentiment_analyzer": settings.SENTIMENT_MODEL_NAME,
        },
        "fallback_modes": {
            "local_fallback_store_enabled": settings.ENABLE_LOCAL_FALLBACK_STORE,
            "is_fallback_active": fallback_active,
        },
    }
