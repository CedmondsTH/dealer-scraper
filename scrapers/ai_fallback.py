"""
AI-powered fallback scraper using Google Gemini.

This module provides intelligent extraction capabilities for websites
that don't match any hardcoded patterns, using Gemini AI for analysis.
"""

import json
import re
from typing import List
from bs4 import BeautifulSoup
import google.generativeai as genai

from scrapers.base import BaseScraper
from models.dealership import DealershipData
from config.settings import config
from utils.logging import logger, log_gemini_success


class AIFallbackScraper(BaseScraper):
    """AI-powered scraper using Google Gemini for intelligent extraction."""
    
    def __init__(self):
        super().__init__("AI Fallback (Gemini)")
        self._configure_ai()
    
    def _configure_ai(self):
        """Configure Google Gemini AI."""
        if not config.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not found. AI fallback will be disabled.")
            self.model = None
            return
        
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            # Use gemini-1.5-flash model (removed -8b suffix which might be invalid/deprecated)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            logger.error(f"Failed to configure Gemini AI: {e}")
            self.model = None

    def can_handle(self, html: str, url: str) -> bool:
        """AI fallback can handle any website if AI is configured."""
        return self.model is not None
    
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """Extract dealership data using AI analysis."""
        self.logger.ai_fallback_attempt(url)
        
        try:
            # Prepare HTML for AI analysis
            clean_html = self._prepare_html_for_ai(html)
            
            # Generate AI prompt
            prompt = self._create_extraction_prompt(clean_html, url)
            
            # Get AI response
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse AI response
            dealerships = self._parse_ai_response(response_text, url)
            
            if dealerships:
                self.logger.ai_fallback_success(url, len(dealerships))
                # Log success for pattern development
                log_gemini_success(
                    dealer_name=self._extract_dealer_name_from_url(url),
                    url=url,
                    dealers_found=len(dealerships),
                    html_snippet=clean_html[:1000]
                )
            
            return dealerships
            
        except Exception as e:
            self.logger.error(f"AI fallback failed for {url}: {e}")
            return []
    
    def _prepare_html_for_ai(self, html: str) -> str:
        """Prepare HTML for AI analysis by cleaning and truncating."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove noise elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # Get cleaned HTML and truncate to stay within token limits
        clean_html = str(soup)[:15000]
        return clean_html
    
    def _create_extraction_prompt(self, html: str, url: str) -> str:
        """Create prompt for AI extraction."""
        dealer_name = self._extract_dealer_name_from_url(url)
        
        return f"""
Analyze this HTML from {dealer_name}'s website ({url}) and extract dealership location information.

Extract each dealership/location as a JSON object with these fields:
- name: Full dealership name
- street: Street address  
- city: City name
- state: State/province (2-letter code if possible)
- zip: Postal/ZIP code
- phone: Phone number (clean format)
- website: Website URL (use provided URL if specific dealership site not found)

Return ONLY a valid JSON array of dealership objects. No explanation or additional text.

HTML content:
{html}
"""
    
    def _parse_ai_response(self, response_text: str, url: str) -> List[DealershipData]:
        """Parse AI response and convert to DealershipData objects."""
        # Clean response - remove markdown formatting if present
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        self.logger.debug(f"AI response: {response_text[:200]}...")
        
        try:
            # Parse JSON response
            dealers_data = json.loads(response_text)
            
            if not isinstance(dealers_data, list):
                dealers_data = [dealers_data] if isinstance(dealers_data, dict) else []
            
            # Convert to DealershipData objects
            dealerships = []
            for data in dealers_data:
                if isinstance(data, dict):
                    dealership = DealershipData.from_dict(data, page_url=url)
                    dealerships.append(dealership)
            
            return dealerships
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI response as JSON: {e}")
            return []
    
    def _extract_dealer_name_from_url(self, url: str) -> str:
        """Extract dealer name from URL for logging purposes."""
        # Simple heuristic to extract dealer name from URL
        domain = url.split('/')[2] if '//' in url else url
        # Remove common prefixes/suffixes
        name = domain.replace('www.', '').replace('.com', '').replace('.net', '')
        # Convert to title case
        return name.replace('-', ' ').replace('_', ' ').title()