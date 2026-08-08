"""SupportFlow AI Configuration Settings."""
import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application and AI configuration settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    KNOWLEDGE_BASE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent / "knowledge_base"
    )
    FAISS_INDEX_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent / "data" / "faiss_index"
    )

    # Database Configuration
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", f"sqlite:///{Path(__file__).resolve().parent.parent / 'data' / 'supportflow.db'}")
    )

    # JWT Authentication & Security
    JWT_SECRET_KEY: str = Field(
        default="supportflow-super-secret-jwt-token-key-2026-production-grade"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # OpenAI / LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    LLM_TEMPERATURE: float = 0.0

    # RAG / Retrieval Configuration
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 60
    TOP_K_RETRIEVAL: int = 3
    SIMILARITY_SCORE_THRESHOLD: float = 0.70

    # Application & Logging
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Rate Limiting (Requests per minute)
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def has_valid_api_key(self) -> bool:
        """Checks if a valid, non-placeholder OpenAI API key is configured."""
        key = self.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        if not key or not isinstance(key, str):
            return False
        k = key.strip()
        if k.startswith("${") or k.startswith("your_") or len(k) < 20:
            return False
        return k.startswith("sk-")


# Singleton instance
settings = Settings()
