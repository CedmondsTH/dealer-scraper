"""
User interface package.

This package contains the Streamlit web interface for the
dealer scraping application.
"""

from .streamlit_app import create_app

__all__ = ['create_app']