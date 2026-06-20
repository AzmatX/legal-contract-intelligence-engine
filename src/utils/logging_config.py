"""Logging configuration for Contract Intelligence System."""

import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger
from src.config import settings


def setup_logging(level: str | None = None) -> logging.Logger:
    """Set up application logging with JSON formatting.
    
    Args:
        level: Logging level override. If None, uses settings.log_level.
        
    Returns:
        Configured logger instance.
    """
    log_level = level or settings.log_level
    
    # Create logger
    logger = logging.getLogger("contract_intelligence")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # JSON formatter for production
    if settings.debug:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logging()
