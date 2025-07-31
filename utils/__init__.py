"""Utilities package for the Dealership Scraper."""

from .logging import logger
from .browser import browser_manager
from .parsers import parse_address, extract_phone_number

__all__ = ['logger', 'browser_manager', 'parse_address', 'extract_phone_number']