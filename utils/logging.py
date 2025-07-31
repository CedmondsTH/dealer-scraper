"""
Logging utilities for the application.

This module provides structured logging capabilities with
configurable levels and output formats.
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from config.settings import config


class ScraperLogger:
    """Custom logger for the scraper application."""
    
    def __init__(self, name: str = "dealership_scraper"):
        self.logger = logging.getLogger(name)
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure logger with appropriate handlers and formatters."""
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Set level from config
        level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def scrape_start(self, dealer_name: str, url: str):
        """Log scraping start."""
        self.info(f"Starting scrape for {dealer_name}: {url}")
    
    def scrape_complete(self, dealer_name: str, count: int):
        """Log scraping completion."""
        self.info(f"Scrape complete for {dealer_name}: {count} dealerships found")
    
    def pattern_success(self, pattern_name: str, count: int):
        """Log successful pattern extraction."""
        self.info(f"Pattern '{pattern_name}' found {count} dealerships")
    
    def ai_fallback_attempt(self, dealer_name: str):
        """Log AI fallback attempt."""
        self.info(f"Attempting AI fallback for {dealer_name}")
    
    def ai_fallback_success(self, dealer_name: str, count: int):
        """Log AI fallback success."""
        self.info(f"AI fallback successful for {dealer_name}: {count} dealerships found")


# Global logger instance
logger = ScraperLogger()


def log_gemini_success(dealer_name: str, url: str, dealers_found: int, html_snippet: str = ""):
    """Log when Gemini successfully finds dealerships for pattern development."""
    import csv
    import os
    from config.settings import config
    
    log_file = config.GEMINI_SUCCESS_LOG
    file_exists = os.path.exists(log_file)
    
    try:
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'dealer_group', 'url', 'dealers_found', 'html_snippet'])
            
            writer.writerow([
                datetime.now().isoformat(),
                dealer_name,
                url,
                dealers_found,
                html_snippet[:500] + "..." if len(html_snippet) > 500 else html_snippet
            ])
        
        logger.debug(f"Logged Gemini success for {dealer_name} - {dealers_found} dealers found")
    except Exception as e:
        logger.error(f"Failed to log Gemini success: {e}")