"""
Scrapers package for dealer location extraction.

This package contains the scraper framework and specific
implementations for different dealer website types.
"""

from .base_scraper import BaseScraper, ScraperStrategy
from .scraper_registry import ScraperRegistry, scraper_registry

__all__ = [
    'BaseScraper', 'ScraperStrategy', 
    'ScraperRegistry', 'scraper_registry'
]