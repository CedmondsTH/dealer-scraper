"""
Streamlit web interface for the dealer scraping application.

This module provides a clean, user-friendly web interface
for scraping dealer locations with proper error handling.
"""

import streamlit as st
from typing import Optional
import logging
from pathlib import Path

from config import get_settings, setup_logging
from core.scraper_service import ScraperService, ScrapingStatus
from core.data_service import DataService


class StreamlitApp:
    """Main Streamlit application class."""
    
    def __init__(self):
        self.settings = get_settings()
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        self.scraper_service = ScraperService()
        self.data_service = DataService()
        
        # Initialize session state
        if "scrape_cache" not in st.session_state:
            st.session_state.scrape_cache = {}
    
    def setup_page_config(self) -> None:
        """Configure the Streamlit page."""
        st.set_page_config(
            page_title=self.settings.ui.page_title,
            page_icon=self.settings.ui.page_icon,
            layout=self.settings.ui.layout
        )
    
    def render_header(self) -> None:
        """Render the application header."""
        # Logo
        if Path(self.settings.ui.logo_path).exists():
            st.image(self.settings.ui.logo_path, width=200)
        
        st.title(self.settings.ui.page_title)
        
        # Add some helpful info
        with st.expander("ℹ️ How to use this tool"):
            st.markdown("""
            1. **Enter the dealer group name** (e.g., "Lithia Motors", "AutoNation")
            2. **Paste the locations page URL** from the dealer's website
            3. **Click "Extract Dealerships"** to start scraping
            4. **Download the results** as Excel or CSV when complete
            
            **Supported formats:** JSON-LD, JavaScript variables, and various HTML structures
            """)
    
    def render_input_form(self) -> tuple[str, str]:
        """Render the input form and return dealer name and URL."""
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            dealer_name = st.text_input(
                "Dealer Group Name",
                placeholder="e.g., Lithia Motors",
                help="Enter the name of the dealer group you want to scrape"
            )
        
        with col2:
            url = st.text_input(
                "Dealer Locations Page URL",
                placeholder="https://www.example.com/locations",
                help="Enter the URL of the page that lists dealer locations"
            )
        
        return dealer_name, url
    
    def render_advanced_options(self) -> dict:
        """Render advanced options and return settings."""
        
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                headless = st.checkbox(
                    "Headless Mode",
                    value=self.settings.scraping.headless,
                    help="Run browser without visible window (recommended)"
                )
                
                timeout = st.number_input(
                    "Timeout (seconds)",
                    min_value=10,
                    max_value=300,
                    value=self.settings.scraping.timeout // 1000,
                    help="Maximum time to wait for page to load"
                )
            
            with col2:
                enable_debug = st.checkbox(
                    "Debug Mode",
                    value=self.settings.debug,
                    help="Enable detailed logging and save debug files"
                )
                
                clear_cache = st.button(
                    "Clear Cache",
                    help="Clear cached scraping results"
                )
                
                if clear_cache:
                    st.session_state.scrape_cache.clear()
                    st.success("Cache cleared!")
        
        return {
            'headless': headless,
            'timeout': timeout * 1000,  # Convert to milliseconds
            'debug': enable_debug
        }
    
    def scrape_dealers(self, dealer_name: str, url: str, options: dict) -> Optional[list]:
        """Scrape dealers with caching and proper error handling."""
        
        # Check cache first
        cache_key = f"{dealer_name}_{url}"
        if self.settings.ui.cache_enabled and cache_key in st.session_state.scrape_cache:
            st.info("ℹ️ Using cached results (click 'Clear Cache' in Advanced Options to refresh)")
            return st.session_state.scrape_cache[cache_key]
        
        # Show progress
        with st.spinner("🔍 Scraping dealerships..."):
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Update progress
                progress_bar.progress(25)
                status_text.text("Fetching page content...")
                
                # Perform scraping
                result = self.scraper_service.scrape_dealer_locations(dealer_name, url)
                
                progress_bar.progress(75)
                status_text.text("Processing dealer data...")
                
                # Handle results
                if result.status == ScrapingStatus.FAILED:
                    st.error(f"❌ {result.message}")
                    if result.error:
                        with st.expander("Error Details"):
                            st.text(result.error)
                    return None
                
                elif result.status == ScrapingStatus.NO_DATA:
                    st.warning(f"⚠️ {result.message}")
                    st.info("This could mean:")
                    st.markdown("""
                    - The website structure is not supported yet
                    - The page doesn't contain dealer location data
                    - The data is loaded dynamically and needs special handling
                    """)
                    return None
                
                else:
                    # Success!
                    progress_bar.progress(100)
                    status_text.text("Complete!")
                    
                    # Cache results
                    if self.settings.ui.cache_enabled:
                        st.session_state.scrape_cache[cache_key] = result.dealers
                    
                    return result.dealers
                    
            except Exception as e:
                self.logger.error(f"Unexpected error in UI: {str(e)}", exc_info=True)
                st.error(f"❌ Unexpected error: {str(e)}")
                return None
            
            finally:
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
    
    def render_results(self, dealers: list, dealer_name: str) -> None:
        """Render the results table and download options."""
        
        if not dealers:
            return
        
        # Success message
        st.success(f"✅ Successfully extracted {len(dealers)} dealer locations!")
        
        # Create DataFrame
        df = self.data_service.create_dataframe(dealers)
        
        # Display summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Dealers", len(dealers))
        
        with col2:
            unique_states = df['State/Province'].nunique() if 'State/Province' in df.columns else 0
            st.metric("States/Provinces", unique_states)
        
        with col3:
            franchised_count = len([d for d in dealers if d.get('Dealership Type') == 'Franchised'])
            st.metric("Franchised Dealers", franchised_count)
        
        with col4:
            unique_brands = df['Car Brand'].str.split(';').explode().nunique() if 'Car Brand' in df.columns else 0
            st.metric("Car Brands", unique_brands)
        
        # Display data table
        st.dataframe(df, use_container_width=True)
        
        # Download options
        st.markdown("### 📥 Download Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            excel_buffer = self.data_service.export_to_excel(dealers)
            st.download_button(
                label="📄 Download Excel",
                data=excel_buffer,
                file_name=f"{dealer_name}_locations.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            # CSV download
            csv_data = self.data_service.export_to_csv(dealers)
            st.download_button(
                label="📑 Download CSV",
                data=csv_data.encode('utf-8'),
                file_name=f"{dealer_name}_locations.csv",
                mime="text/csv"
            )
    
    def run(self) -> None:
        """Run the main application."""
        
        # Setup page
        self.setup_page_config()
        self.render_header()
        
        # Input form
        dealer_name, url = self.render_input_form()
        
        # Advanced options
        options = self.render_advanced_options()
        
        # Scraping button and logic
        if st.button("🚀 Extract Dealerships", type="primary"):
            
            # Validation
            if not dealer_name.strip():
                st.error("Please enter a dealer group name")
                return
            
            if not url.strip():
                st.error("Please enter a URL")
                return
            
            # Basic URL validation
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                st.error("Please enter a valid URL (include http:// or https://)")
                return
            
            # Perform scraping
            dealers = self.scrape_dealers(dealer_name.strip(), url.strip(), options)
            
            # Show results
            if dealers:
                self.render_results(dealers, dealer_name.strip())
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666;'>"
            "Built with ❤️ for automotive industry professionals"
            "</div>",
            unsafe_allow_html=True
        )


def create_app() -> StreamlitApp:
    """Create and return a configured Streamlit app instance."""
    return StreamlitApp()


def main() -> None:
    """Main entry point for the Streamlit app."""
    app = create_app()
    app.run()


if __name__ == "__main__":
    main()