from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings configured via environment variables or .env file.
    Follows 12-factor configuration principles using pydantic-settings.
    """

    # Project metadata
    PROJECT_NAME: str = "Multimodal Resume Intelligence & Screening Studio"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Cross-Origin Resource Sharing (CORS)
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Database Configuration (MongoDB Atlas & Local JSON Fallback)
    MONGODB_URI: str = "mongodb+srv://sample_user:sample_password@cluster0.mongodb.net/?retryWrites=true&w=majority"
    MONGODB_DB_NAME: str = "multimodal_resume_intel"
    ENABLE_LOCAL_FALLBACK_STORE: bool = True
    FALLBACK_DATA_DIR: str = "./data/fallback_store"

    # Multimodal & NLP Model Configuration
    WHISPER_MODEL_SIZE: str = "base"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    SENTIMENT_MODEL_NAME: str = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json

                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


# Global settings singleton
settings = Settings()
