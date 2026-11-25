import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import api_router
from backend.app.api.routes.health import health_check
from backend.app.core.config import settings
from backend.app.core.database import db_manager

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context: handles startup and shutdown logic."""
    logger.info(f"Starting {settings.PROJECT_NAME}...")
    await db_manager.connect_to_mongo()
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    await db_manager.close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent multimodal resume screening, Whisper speech analytics, and candidate ranking platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Support both /api and /api/v1 prefixes
app.include_router(api_router, prefix="/api")
if settings.API_V1_STR != "/api":
    app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
async def root_health():
    """Root health endpoint reporting API status, Atlas connectivity, and model modes."""
    return await health_check()


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
        "health_check": "/health",
    }
