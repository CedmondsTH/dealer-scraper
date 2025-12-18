"""
Dealer Location Scraper - Streamlit Web Application

A professional web application for extracting dealer location data
from automotive dealer websites with clean, validated output.
"""

import streamlit as st
import pandas as pd
import logging
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our modules
from src.services.scraper_service import ScraperService, ScrapingStatus
from src.services.data_service import DataService
from src.config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DealerScraperApp:
    """Main Streamlit application for dealer scraping."""
    
    def __init__(self):
        self.scraper_service = ScraperService()
        self.data_service = DataService()
        
        # Initialize session state
        if "scrape_cache" not in st.session_state:
            st.session_state.scrape_cache = {}
    
    def setup_page(self):
        """Configure the Streamlit page with custom styling."""
        st.set_page_config(
            page_title=config.PAGE_TITLE,
            page_icon=config.PAGE_ICON,
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for "World Class" look
        st.markdown("""
        <style>
        .main {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 1px solid #333;
            background-color: #262730;
            color: #fff;
        }
        .metric-card {
            background-color: #262730;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #333;
            text-align: center;
        }
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar."""
        with st.sidebar:
            st.title(f"{config.PAGE_ICON} Dealer Scraper")
            st.markdown("---")
            
            st.markdown("### 📜 History")
            if st.session_state.scrape_cache:
                for key in st.session_state.scrape_cache.keys():
                    dealer_name = key.split('_')[0]
                    if st.button(f"Load {dealer_name}", key=f"hist_{key}"):
                        st.session_state.current_view = key
            else:
                st.info("No recent scrapes.")
            
            st.markdown("---")
            st.markdown("### ⚙️ Settings")
            with st.expander("Advanced Options"):
                if st.button("Clear Cache"):
                    st.session_state.scrape_cache.clear()
                    st.success("Cache cleared!")
            
            st.markdown("---")
            st.caption(f"v3.0.0 | Built for Auto Retail")

    def render_header(self):
        """Render the application header."""
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("Dealer Location Intelligence")
            st.markdown("Extract, validate, and export dealer network data with enterprise-grade precision.")
        with col2:
            # Placeholder for a logo or status indicator
            st.success("System Operational")
    
    def render_input_form(self) -> tuple[str, str]:
        """Render the input form."""
        with st.container():
            st.markdown("### 🎯 New Extraction Task")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                dealer_name = st.text_input(
                    "Dealer Group Name",
                    placeholder="e.g., Lithia Motors",
                    help="Enter the name of the dealer group"
                )
            
            with col2:
                url = st.text_input(
                    "Target URL",
                    placeholder="https://www.example.com/locations",
                    help="Enter the URL of the page that lists dealer locations"
                )
            
            return dealer_name, url
    
    def scrape_dealers(self, dealer_name: str, url: str) -> Optional[list]:
        """Scrape dealers with progress tracking."""
        
        cache_key = f"{dealer_name}_{url}"
        if cache_key in st.session_state.scrape_cache:
            st.info("⚡ Using cached results")
            return st.session_state.scrape_cache[cache_key]
        
        # Progress UI
        progress_container = st.empty()
        with progress_container.container():
            st.markdown("### 🔄 Processing...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                def update_progress(percent, message):
                    progress_bar.progress(percent)
                    status_text.markdown(f"**{message}**")

                result = self.scraper_service.scrape_dealer_locations(dealer_name, url, progress_callback=update_progress)
                
                if result.status == ScrapingStatus.FAILED:
                    st.error(f"❌ {result.message}")
                    if result.error:
                        st.code(result.error, language="text")
                    return None
                
                elif result.status == ScrapingStatus.NO_DATA:
                    st.warning(f"⚠️ {result.message}")
                    return None
                
                else:
                    st.session_state.scrape_cache[cache_key] = result.dealers
                    return result.dealers
                    
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                st.error(f"❌ Unexpected error: {str(e)}")
                return None
            finally:
                progress_container.empty()

    def render_results(self, dealers: list, dealer_name: str):
        """Render results and download options."""
        if not dealers:
            return
        
        st.divider()
        st.markdown(f"### ✅ Extraction Complete: {dealer_name}")
        
        # Metrics
        df = self.data_service.create_dataframe(dealers)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Locations", len(dealers))
        with col2:
            unique_states = df['State/Province'].nunique() if 'State/Province' in df.columns else 0
            st.metric("States Covered", unique_states)
        with col3:
            franchised_count = len([d for d in dealers if d.get('Dealership Type') == 'Franchised'])
            st.metric("Franchised Dealers", franchised_count)
        with col4:
            if 'Car Brand' in df.columns:
                unique_brands = df['Car Brand'].str.split(';').explode().nunique()
            else:
                unique_brands = 0
            st.metric("Brands Detected", unique_brands)
        
        # Data Preview
        with st.expander("📊 Data Preview", expanded=True):
            st.dataframe(df, use_container_width=True, height=400)
        
        # Downloads
        st.markdown("### 📥 Export Data")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            excel_buffer = self.data_service.export_to_excel(dealers)
            st.download_button(
                label="📄 Download Excel",
                data=excel_buffer,
                file_name=f"{dealer_name}_locations.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            csv_data = self.data_service.export_to_csv(dealers)
            st.download_button(
                label="📑 Download CSV",
                data=csv_data.encode('utf-8'),
                file_name=f"{dealer_name}_locations.csv",
                mime="text/csv",
                use_container_width=True
            )

    def run(self):
        """Run the main application."""
        self.setup_page()
        self.render_sidebar()
        self.render_header()
        
        dealer_name, url = self.render_input_form()
        
        if st.button("🚀 Start Extraction", type="primary"):
            if not dealer_name.strip() or not url.strip():
                st.error("Please provide both a Dealer Name and a URL.")
                return
                
            dealers = self.scrape_dealers(dealer_name.strip(), url.strip())
            if dealers:
                self.render_results(dealers, dealer_name.strip())

def main():
    try:
        app = DealerScraperApp()
        app.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()