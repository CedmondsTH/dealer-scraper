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
            
    def render_header(self):
        """Render application header."""
        # Display logo if available
        try:
            st.image("trackhawk_logo.png", width=200)
        except:
            pass  # Logo file not found
        
        st.title("🚗 Dealership Data Scraper")
        st.markdown("**Professional automotive dealership data extraction platform**")
        
        # Add features overview
        with st.expander("ℹ️ Features & Capabilities"):
            st.markdown("""
            - **🤖 AI-Powered**: Gemini AI fallback for unlimited website support
            - **📊 Multi-Format Export**: Excel, CSV, and JSON output
            - **🎯 Smart Recognition**: 12+ pre-built dealership group patterns
            - **🔍 Intelligent Parsing**: Advanced address and contact extraction
            - **📈 Real-Time Processing**: Live progress tracking
            """)
    
    def render_input_form(self):
        """Render the main input form."""
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
                    value=config.MAX_DEALERSHIPS,
                    help="Maximum number of dealerships to extract"
                )
            with col2:
                # Check if API key is available
                has_api_key = bool(config.GEMINI_API_KEY)
                
                use_ai_fallback = st.checkbox(
                    "Enable AI Fallback", 
                    value=has_api_key,
                    disabled=not has_api_key,
                    help="Use AI when standard patterns don't work" if has_api_key else "GEMINI_API_KEY required for AI fallback"
                )
                
                if not has_api_key:
                    st.caption("⚠️ GEMINI_API_KEY not set")
        
        return dealer_name, url, max_dealerships, use_ai_fallback
    
    def render_extraction_button(self, dealer_name: str, url: str) -> bool:
        """Render extraction button and handle validation."""
        # Validation
        if not dealer_name.strip():
            st.warning("⚠️ Please enter a dealer group name")
            return False
        
        if not url.strip():
            st.warning("⚠️ Please enter a locations page URL")
            return False
        
        if not url.startswith(('http://', 'https://')):
            st.warning("⚠️ URL must start with http:// or https://")
            return False
        
        # Extraction button
        return st.button(
            "🚀 Extract Dealerships", 
            type="primary",
            use_container_width=True,
            help="Start the dealership extraction process"
        )
    
    def scrape_with_subprocess(self, dealer_name: str, url: str) -> pd.DataFrame:
        """
        Run scraping in subprocess to avoid blocking UI.
        
        Args:
            dealer_name: Name of dealer group
            url: URL to scrape
            
        Returns:
            DataFrame with extracted dealership data
        """
        # Check cache first
        cache_key = f"{dealer_name}_{url}"
        if cache_key in st.session_state.scrape_cache:
            return st.session_state.scrape_cache[cache_key]
        
        try:
            # Create a temporary file for output
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
                output_path = temp_file.name
            
            # Run CLI version in subprocess with output file argument
            cmd = [sys.executable, "main.py", dealer_name, url, output_path]
            
            with st.spinner("🔍 Extracting dealership data..."):
                # Progress tracking
                status_container = st.empty()
                
                # Run subprocess
                proc = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True,
                    encoding='utf-8',
                    bufsize=1
                )
                
                # Read stderr line by line for progress
                stderr_output = []
                while True:
                    line = proc.stderr.readline()
                    if not line:
                        if proc.poll() is not None:
                            break
                        continue
                        
                    stderr_output.append(line)
                    status_container.info(f"Status: {line.strip()}")
                    logger.info(f"Subprocess log: {line.strip()}")
                
                stdout, _ = proc.communicate()
                stderr = "".join(stderr_output)
                
                if proc.returncode != 0:
                    st.error("❌ Extraction failed. See details below.")
                    st.text(stderr)
                    if os.path.exists(output_path):
                        os.unlink(output_path)
                    raise RuntimeError("Scraping subprocess failed")
                
                # Read results from file
                try:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if not content.strip():
                            rows = []
                        else:
                            rows = json.loads(content)
                finally:
                    # Clean up temp file
                    if os.path.exists(output_path):
                        os.unlink(output_path)
                
                df = self._process_dataframe(rows, dealer_name)
                
                # Cache results
                st.session_state.scrape_cache[cache_key] = df
                
                return df
                
        except Exception as e:
            st.error(f"❌ Extraction error: {e}")
            logger.error(f"Streamlit extraction failed: {e}")
            raise
    
    def _process_dataframe(self, rows: list, dealer_name: str) -> pd.DataFrame:
        """Process raw extraction data into formatted DataFrame."""
        if not rows:
            return pd.DataFrame()
        
        df = pd.DataFrame(rows)
        
        # Add dealer group
        df["Dealer Group"] = dealer_name
        
        # Apply classification if needed
        if "name" in df.columns and "Dealership Type" not in df.columns:
            df["Dealership Type"] = df["name"].apply(
                lambda x: self._classify_dealership(x)
            )
        
        # Set country based on state/province
        if "state" in df.columns and "Country" not in df.columns:
            df["Country"] = df["state"].apply(
                lambda x: "Canada" if str(x).strip() in Constants.CANADIAN_PROVINCES 
                         else "United States of America"
            )
        
        # Extract car brands
        if "name" in df.columns and "Car Brand" not in df.columns:
            df["Car Brand"] = df["name"].apply(self._extract_car_brands)
        
        # Standardize column names
        rename_map = {
            "name": "Dealership",
            "street": "Address", 
            "city": "City",
            "state": "State/Province",
            "zip": "Postal Code",
            "phone": "Phone",
            "website": "Website"
        }
        df.rename(columns=rename_map, inplace=True, errors="ignore")
        
        # Reorder columns
        df = self._reorder_columns(df)
        
        return df
    
    def _classify_dealership(self, name: str) -> str:
        """Classify dealership type based on name."""
        if not isinstance(name, str):
            return 'Unknown'
        
        name_lower = name.lower()
        
        # Check each category
        if any(word in name_lower for word in Constants.COLLISION_KEYWORDS):
            return 'Collision'
        elif any(word in name_lower for word in Constants.FIXED_OPS_KEYWORDS):
            return 'Fixed Ops'
        elif any(word in name_lower for word in Constants.USED_CAR_KEYWORDS):
            return 'Used'
        elif any(brand.lower() in name_lower for brand in Constants.CAR_BRANDS):
            return 'Franchised'
        else:
            return 'Unknown'
    
    def _extract_car_brands(self, name: str) -> str:
        """Extract car brands from dealership name."""
        if not isinstance(name, str):
            return ""
        
        name_lower = name.lower()
        
        # Check for special combinations
        if all(word in name_lower for word in ['chrysler', 'jeep', 'dodge', 'ram', 'fiat']):
            return 'CDJRF'
        elif all(word in name_lower for word in ['chrysler', 'jeep', 'dodge', 'ram']):
            return 'CDJR'
        else:
            found_brands = [brand for brand in Constants.CAR_BRANDS 
                          if brand.lower() in name_lower]
            return "; ".join(found_brands) if found_brands else ""
    
    def _reorder_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reorder columns according to standard output format."""
        # Get columns that exist in the DataFrame
        available_cols = [col for col in Constants.OUTPUT_COLUMNS if col in df.columns]
        other_cols = [col for col in df.columns if col not in available_cols]
        
        return df[available_cols + other_cols]
    
    def render_results(self, df: pd.DataFrame, dealer_name: str):
        """Render extraction results and download options."""
        if df.empty:
            st.error("❌ No dealerships found. Please check the URL and try again.")
            return
        
        # Success message
        st.success(f"✅ Successfully extracted {len(df)} dealerships!")
        
        # Results overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Locations", len(df))
        with col2:
            franchised_count = len(df[df.get('Dealership Type', '') == 'Franchised'])
            st.metric("Franchised Dealers", franchised_count)
        with col3:
            unique_brands = len(df[df.get('Car Brand', '') != '']['Car Brand'].str.split('; ').explode().unique())
            st.metric("Unique Brands", unique_brands)
        
        # Data preview
        st.markdown("### 📊 Extracted Data")
        st.dataframe(df, use_container_width=True, height=400)
        
        # Download options
        st.markdown("### 📥 Download Options")
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            excel_buffer = self._create_excel_file(df)
            st.download_button(
                "📄 Download Excel",
                data=excel_buffer,
                file_name=f"{dealer_name}_dealerships.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # CSV download
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📑 Download CSV",
                data=csv_data,
                file_name=f"{dealer_name}_dealerships.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    def _create_excel_file(self, df: pd.DataFrame) -> BytesIO:
        """Create Excel file from DataFrame."""
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Dealerships")
        buffer.seek(0)
        return buffer
    
    def render_footer(self):
        """Render application footer."""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
        <p>🚗 <strong>Dealership Data Scraper</strong></p>
        <p>Powered by AI • Streamlit • Python</p>
        </div>
        """, unsafe_allow_html=True)
    
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