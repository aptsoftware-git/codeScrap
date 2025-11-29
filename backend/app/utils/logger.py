"""
Logging configuration using loguru.
"""

import sys
from pathlib import Path
from loguru import logger
from app.config import settings


def setup_logging():
    """Configure logging for the application."""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Add file handler
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="1 week",
        compression="zip"
    )
    
    logger.info("Logging configured successfully")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Log file: {settings.log_file}")
