"""
Logging configuration for the application.

This module provides centralized logging setup with proper
formatters, handlers, and rotation policies.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from .settings import LoggingSettings


def setup_logging(settings: Optional[LoggingSettings] = None) -> None:
    """
    Setup application logging with the given settings.
    
    Args:
        settings: Logging settings. If None, will use default settings.
    """
    if settings is None:
        from .settings import get_settings
        settings = get_settings().logging
    
    # Create formatter
    formatter = logging.Formatter(settings.format)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.level))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.level))
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if settings.file_path:
        try:
            # Ensure directory exists
            log_path = Path(settings.file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                settings.file_path,
                maxBytes=settings.max_file_size,
                backupCount=settings.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, settings.level))
            root_logger.addHandler(file_handler)
            
            logging.info(f"Logging to file: {settings.file_path}")
            
        except Exception as e:
            logging.warning(f"Failed to setup file logging: {e}")
    
    # Setup specific loggers with appropriate levels
    _setup_library_loggers()
    
    logging.info("Logging system initialized")


def _setup_library_loggers() -> None:
    """Configure logging levels for third-party libraries."""
    
    # Reduce noise from third-party libraries
    library_loggers = {
        'urllib3': logging.WARNING,
        'requests': logging.WARNING,
        'playwright': logging.WARNING,
        'selenium': logging.WARNING,
        'asyncio': logging.WARNING,
    }
    
    for logger_name, level in library_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the given name.
    
    Args:
        name: Name for the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)