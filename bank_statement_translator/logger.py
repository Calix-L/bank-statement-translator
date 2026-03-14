"""Logging configuration for bank statement translator."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from config import get_settings


def setup_logger(
    name: str = "bank_statement_translator",
    level: int | None = None,
    log_file: str | None = None,
) -> logging.Logger:
    """Setup and return a configured logger.
    
    Args:
        name: Logger name
        level: Logging level (default: from settings or INFO)
        log_file: Log file path (default: from settings or None)
        
    Returns:
        Configured logger instance
    """
    # Get settings for defaults
    settings = get_settings()
    
    # Determine log level
    if level is None:
        level_str = settings.log_level.upper()
        level = getattr(logging, level_str, logging.INFO)
    
    # Determine log file
    if log_file is None:
        log_file = settings.log_file
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
        
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "bank_statement_translator") -> logging.Logger:
    """Get an existing logger or create a new one.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
