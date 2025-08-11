"""
Configuration management package.

This package provides configuration management for the dealer
scraping application including settings, logging, and environment setup.
"""

from .settings import Settings, get_settings
from .logging_config import setup_logging

__all__ = ['Settings', 'get_settings', 'setup_logging']