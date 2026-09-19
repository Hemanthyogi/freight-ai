"""
FreightMind AI — Structured Logger
src/utils/logger.py

Provides a pre-configured loguru logger.
Import `logger` from this module throughout the project.
"""

import sys
from loguru import logger


def setup_logger(level: str = "INFO", log_file: str | None = None) -> None:
    """
    Configure loguru logger.

    Args:
        level:    Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to also write logs to.
    """
    logger.remove()   # Remove default handler

    # Console handler — human-readable format
    logger.add(
        sys.stderr,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File handler — structured JSON (optional)
    if log_file:
        logger.add(
            log_file,
            level=level,
            format="{time} | {level} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="7 days",
            compression="gz",
        )


# ── Auto-configure on import ─────────────────────────────────────────────────
# Can be overridden by calling setup_logger() again in main.py
setup_logger(level="INFO")

__all__ = ["logger", "setup_logger"]
