"""
Streamlit user interface for the Dealership Scraper.

This module provides the web-based user interface for the scraper
with input forms, progress tracking, and download capabilities.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
import sys
import subprocess
import json

from config.settings import config, Constants
from utils.logging import logger


class StreamlitUI:
    """Manages the Streamlit user interface."""
    
    def __init__(self):
        self.setup_page_config()
        self.setup_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Dealership Data Scraper", 
            layout="centered",
            initial_sidebar_state="collapsed"
        )
    
    def setup_session_state(self):
        """Initialize session state variables."""
        # Ensure scrape_cache is always initialized
        if "scrape_cache" not in st.session_state:
            st.session_state.scrape_cache = {}
            
    def run(self):
        """Run the complete Streamlit application."""
        # Ensure session state is set up at the start of every run
        self.setup_session_state()
        
        try:
            # Validate configuration
            config.validate()
            
            # Render UI components
            self.render_header()
            
            # Main form
            dealer_name, url, max_dealerships, use_ai_fallback = self.render_input_form()
            
            # Extract button and processing
            if self.render_extraction_button(dealer_name, url):
                try:
                    df = self.scrape_with_subprocess(dealer_name, url)
                    self.render_results(df, dealer_name)
                except Exception as e:
                    st.error(f"❌ Extraction failed: {e}")
            
            # Footer
            self.render_footer()
            
        except ValueError as e:
            st.error(f"❌ Configuration Error: {e}")
            st.info("💡 Please check your environment variables, especially GEMINI_API_KEY")


# Global UI instance
ui = StreamlitUI()