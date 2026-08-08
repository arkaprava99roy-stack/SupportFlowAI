"""Logging and formatting utilities for SupportFlow AI."""
import logging
import sys
from src.config import settings


def get_logger(name: str = "supportflow") -> logging.Logger:
    """Configures and returns a robust standard logger compatible with all terminal encodings."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(level)

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger


logger = get_logger()
