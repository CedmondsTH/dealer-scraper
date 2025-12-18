"""
Streamlit user interface for the Dealership Scraper.

This module provides a professional web-based interface for scraping
dealer locations with real-time progress tracking and data export.
"""

import streamlit as st
import pandas as pd
import logging
from io import BytesIO
from typing import Optional, Tuple
from pathlib import Path

# Import centralized configuration
from config import config, Constants

# Import services
from src.services.scraper_service import ScraperService, ScrapingStatus
from src.services.data_service import DataService
from src.exceptions import DealerScraperError, ConfigurationError

logger = logging.getLogger(__name__)


class StreamlitUI:
    """Manages the Streamlit user interface."""
    
    def __init__(self):
        """Initialize the UI."""
        self.setup_page_config()
        self.setup_session_state()
        self.scraper_service = ScraperService()
        self.data_service = DataService()
    
    def setup_page_config(self) -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=config.ui.page_title,
            page_icon="🚗",
            layout=config.ui.layout,
            initial_sidebar_state="collapsed"
        )
        
        # Apply custom CSS for professional appearance
        st.markdown("""
        <style>
        .main {
            padding-top: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #0066cc;
            color: white;
            font-weight: 600;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            border: none;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #0052a3;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #0066cc;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def setup_session_state(self) -> None:
        """Initialize session state variables."""
        if "scrape_cache" not in st.session_state:
            st.session_state.scrape_cache = {}
        if "last_result" not in st.session_state:
            st.session_state.last_result = None
    
    def render_header(self) -> None:
        """Render application header with logo and title."""
        # Display logo if available
        logo_path = Path(config.ui.logo_path)
        if logo_path.exists():
            try:
                st.image(str(logo_path), width=200)
            except Exception as e:
                logger.warning(f"Failed to load logo: {e}")
        
        st.title("🚗 Dealer Location Scraper")
        st.markdown("**Professional automotive dealership data extraction platform**")
        
        # Features overview
        with st.expander("ℹ️ Features & Capabilities"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **Scraping Features:**
                - 🤖 AI-Powered fallback extraction
                - 🎯 15+ pre-built dealer patterns
                - 🔄 Automatic retry with Playwright
                - 📍 Sitemap crawling support
                """)
            with col2:
                st.markdown("""
                **Data Quality:**
                - ✅ Address validation & parsing
                - 🔍 Duplicate detection
                - 🏷️ Automatic brand classification
                - 📊 Multiple export formats
                """)
    
    def render_input_form(self) -> Tuple[str, str, int, bool]:
        """
        Render the main input form.
        
        Returns:
            Tuple of (dealer_name, url, max_dealerships, use_ai_fallback)
        """
        st.markdown("### 📝 Extraction Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dealer_name = st.text_input(
                "Dealer Group Name",
                placeholder="e.g., Lithia Motors",
                help="Enter the name of the automotive dealer group"
            )
        
        with col2:
            url = st.text_input(
                "Locations Page URL",
                placeholder="https://dealer-website.com/locations",
                help="URL of the page containing dealership locations"
            )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                max_dealerships = st.number_input(
                    "Max Dealerships",
                    min_value=1,
                    max_value=5000,
                    value=config.data.max_dealers,
                    help="Maximum number of dealerships to extract"
                )
            with col2:
                use_ai_fallback = st.checkbox(
                    "Enable AI Fallback",
                    value=True,
                    help="Use Gemini AI when standard patterns don't work"
                )
        
        return dealer_name, url, max_dealerships, use_ai_fallback
    
    def validate_inputs(self, dealer_name: str, url: str) -> Optional[str]:
        """
        Validate user inputs.
        
        Returns:
            Error message if validation fails, None otherwise
        """
        if not dealer_name.strip():
            return "⚠️ Please enter a dealer group name"
        
        if not url.strip():
            return "⚠️ Please enter a locations page URL"
        
        if not url.startswith(('http://', 'https://')):
            return "⚠️ URL must start with http:// or https://"
        
        return None
    
    def perform_scraping(self, dealer_name: str, url: str) -> Optional[pd.DataFrame]:
        """
        Perform the scraping operation with progress tracking.
        
        Args:
            dealer_name: Name of dealer group
            url: URL to scrape
            
        Returns:
            DataFrame with extracted data, or None if failed
        """
        # Check cache
        cache_key = f"{dealer_name}_{url}"
        if config.ui.cache_enabled and cache_key in st.session_state.scrape_cache:
            logger.info(f"Using cached result for {cache_key}")
            return st.session_state.scrape_cache[cache_key]
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(percent: int, message: str):
            """Update progress bar and status message."""
            progress_bar.progress(percent)
            status_text.text(message)
        
        try:
            # Perform scraping
            update_progress(10, "🔍 Initializing scraper...")
            result = self.scraper_service.scrape_dealer_locations(
                dealer_name,
                url,
                progress_callback=update_progress
            )
            
            if not result.success:
                st.error(f"❌ {result.message}")
                if result.error:
                    with st.expander("Error Details"):
                        st.code(result.error)
                return None
            
            # Process data into DataFrame
            update_progress(95, "📊 Formatting data...")
            df = self.data_service.create_dataframe(result.dealers)
            
            # Final deduplication at UI level (safety measure)
            # Drop duplicates based on dealership name, address, and city
            dedup_cols = []
            for col in ['Dealership', 'Address', 'City']:
                if col in df.columns:
                    dedup_cols.append(col)
            
            if dedup_cols:
                df = df.drop_duplicates(subset=dedup_cols, keep='first')
            
            # Cache result
            if config.ui.cache_enabled:
                st.session_state.scrape_cache[cache_key] = df
            
            progress_bar.empty()
            status_text.empty()
            
            return df
            
        except DealerScraperError as e:
            st.error(f"❌ Scraping error: {e}")
            logger.error(f"Scraping failed: {e}", exc_info=True)
            return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            logger.error(f"Unexpected error during scraping: {e}", exc_info=True)
            return None
        finally:
            progress_bar.empty()
            status_text.empty()
    
    def render_results(self, df: pd.DataFrame, dealer_name: str) -> None:
        """
        Render extraction results with metrics and download options.
        
        Args:
            df: DataFrame with dealer data
            dealer_name: Name of dealer group
        """
        if df.empty:
            st.error("❌ No dealerships found. Please check the URL and try again.")
            return
        
        # Success message
        st.success(f"✅ Successfully extracted {len(df)} dealerships!")
        
        # Metrics
        st.markdown("### 📊 Extraction Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Locations", len(df))
        
        with col2:
            franchised_count = len(df[df.get('Dealership Type', '') == 'Franchised'])
            st.metric("Franchised", franchised_count)
        
        with col3:
            if 'Car Brand' in df.columns:
                unique_brands = len(
                    df[df['Car Brand'] != '']['Car Brand']
                    .str.split('; ')
                    .explode()
                    .unique()
                )
                st.metric("Unique Brands", unique_brands)
            else:
                st.metric("Unique Brands", "N/A")
        
        with col4:
            if 'Country' in df.columns:
                countries = df['Country'].nunique()
                st.metric("Countries", countries)
            else:
                st.metric("Countries", "N/A")
        
        # Data preview
        st.markdown("### 📋 Extracted Data")
        st.dataframe(df, use_container_width=True, height=400)
        
        # Download options
        st.markdown("### 📥 Download Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Excel download
            excel_buffer = self._create_excel_file(df)
            st.download_button(
                label="📄 Download Excel",
                data=excel_buffer,
                file_name=f"{dealer_name.replace(' ', '_')}_dealerships.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # CSV download
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📑 Download CSV",
                data=csv_data,
                file_name=f"{dealer_name.replace(' ', '_')}_dealerships.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            # JSON download
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📦 Download JSON",
                data=json_data,
                file_name=f"{dealer_name.replace(' ', '_')}_dealerships.json",
                mime="application/json",
                use_container_width=True
            )
    
    def _create_excel_file(self, df: pd.DataFrame) -> BytesIO:
        """
        Create Excel file from DataFrame.
        
        Args:
            df: DataFrame to export
            
        Returns:
            BytesIO buffer with Excel file
        """
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Dealerships")
            
            # Auto-adjust column widths
            worksheet = writer.sheets["Dealerships"]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        buffer.seek(0)
        return buffer
    
    def render_footer(self) -> None:
        """Render application footer."""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem 0;'>
            <p style='margin: 0;'><strong>Dealer Location Scraper</strong> v2.0</p>
            <p style='margin: 0.5rem 0 0 0;'>
                Built with Python • Streamlit • Playwright • Gemini AI
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def run(self) -> None:
        """Run the complete Streamlit application."""
        try:
            # Validate configuration
            try:
                config.validate()
            except ConfigurationError as e:
                st.error(f"❌ Configuration Error: {e}")
                st.info("💡 Please set GEMINI_API_KEY in your .env file or environment variables")
                st.stop()
            
            # Render UI components
            self.render_header()
            
            # Main form
            dealer_name, url, max_dealerships, use_ai_fallback = self.render_input_form()
            
            # Validation
            validation_error = self.validate_inputs(dealer_name, url)
            if validation_error:
                st.warning(validation_error)
            
            # Extract button
            if st.button("🚀 Extract Dealerships", type="primary", disabled=bool(validation_error)):
                df = self.perform_scraping(dealer_name, url)
                if df is not None:
                    st.session_state.last_result = (df, dealer_name)
            
            # Display last result if available
            if st.session_state.last_result:
                df, dealer_name = st.session_state.last_result
                self.render_results(df, dealer_name)
            
            # Footer
            self.render_footer()
            
        except Exception as e:
            st.error(f"❌ Application error: {e}")
            logger.error(f"Application error: {e}", exc_info=True)


def run_app() -> None:
    """Entry point for running the Streamlit app."""
    ui = StreamlitUI()
    ui.run()


# For backwards compatibility
if __name__ == "__main__":
    run_app()

