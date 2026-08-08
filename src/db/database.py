"""Database connection and session factory for PostgreSQL / SQLite."""
import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.db.models import Base
from src.config import settings
from src.utils.logger import logger

# Resolve database URL
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    # Ensure local directory exists
    db_file_path = db_url.replace("sqlite:///", "")
    if db_file_path and not db_file_path.startswith(":memory:"):
        Path(db_file_path).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    # PostgreSQL engine with connection pooling
    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(recreate: bool = False) -> None:
    """Creates all database tables defined in models."""
    logger.info(f"Initializing database schema with engine ({engine.url.drivername})...")
    if recreate:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI endpoints and database transactions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
