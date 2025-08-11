"""
Command-line interface package.

This package provides the CLI interface for the dealer
scraping application with proper argument parsing and commands.
"""

from .main import main, cli_main

__all__ = ['main', 'cli_main']