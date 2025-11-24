"""
AI-powered fallback scraper using Google Gemini.

This module provides intelligent extraction capabilities for websites
that don't match any hardcoded patterns, using Gemini AI for analysis.

Features:
- Structure analysis: AI identifies the best extraction strategy
- Direct extraction: AI extracts data directly as a fallback
"""

import json
import re
from typing import List, Optional, Dict, Any
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
            # Use gemini-2.5-flash - latest stable flash model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Configured Gemini AI with gemini-2.5-flash model")
        except Exception as e:
            logger.error(f"Failed to configure Gemini AI: {e}")
            self.model = None

    def can_handle(self, html: str, url: str) -> bool:
        """AI fallback can handle any website if AI is configured."""
        return self.model is not None
    
    def analyze_structure(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Analyze HTML structure and suggest extraction strategy.
        
        This method uses AI to identify patterns in the HTML and suggest
        CSS selectors and extraction approaches without extracting the data itself.
        
        Args:
            html: HTML content to analyze
            url: URL of the page
            
        Returns:
            Dictionary containing extraction strategy, or None if analysis fails
            
        Strategy format:
        {
            "strategy_type": "css_selectors" | "table" | "json_ld" | "schema_org",
            "container_selector": "CSS selector for dealership containers",
            "name_selector": "CSS selector for name (relative to container)",
            "address_selector": "CSS selector for address",
            "city_selector": "CSS selector for city", 
            "state_selector": "CSS selector for state",
            "zip_selector": "CSS selector for ZIP",
            "phone_selector": "CSS selector for phone",
            "website_selector": "CSS selector for website",
            "confidence": 0.0-1.0,
            "notes": "Additional extraction hints"
        }
        """
        if not self.model:
            logger.warning("AI model not configured, cannot analyze structure")
            return None
        
        try:
            logger.info(f"Analyzing HTML structure for {url}")
            
            # Prepare HTML sample for analysis
            html_sample = self._prepare_html_for_structure_analysis(html)
            
            # Create structure analysis prompt
            prompt = self._create_structure_analysis_prompt(html_sample, url)
            
            # Get AI response
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse strategy from response
            strategy = self._parse_strategy_response(response_text)
            
            if strategy:
                confidence = strategy.get('confidence', 0.0)
                logger.info(f"AI suggested strategy for {url} "
                          f"(confidence: {confidence:.2f})")
                return strategy
            else:
                logger.warning(f"AI could not determine strategy for {url}")
                return None
                
        except Exception as e:
            logger.error(f"Structure analysis failed for {url}: {e}")
            return None
    
    def _prepare_html_for_structure_analysis(self, html: str) -> str:
        """
        Prepare HTML sample for structure analysis.
        
        For structure analysis, we want a representative sample that shows
        the pattern without being too large. We'll try to find the "meat"
        of the page where dealership listings are likely to be.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove noise
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
            tag.decompose()
        
        # Try to find the main content area (where dealerships are likely listed)
        # Look for common patterns
        main_content = None
        
        # Try to find main content container
        for selector in ['main', '[role="main"]', '#main', '.main-content', 
                        '#content', '.content', 'article', '.container']:
            main_content = soup.select_one(selector)
            if main_content and len(str(main_content)) > 1000:
                soup = BeautifulSoup(str(main_content), 'html.parser')
                break
        
        # Get a larger sample - 20K chars to ensure we capture repeating patterns
        clean_html = str(soup)[:20000]
        
        # If the sample is too short, it might be an error page
        if len(clean_html) < 500:
            logger.warning(f"HTML sample very short ({len(clean_html)} chars) - might be error page")
        
        return clean_html
    
    def _create_structure_analysis_prompt(self, html: str, url: str) -> str:
        """Create prompt for AI structure analysis."""
        dealer_name = self._extract_dealer_name_from_url(url)
        
        return f"""
You are analyzing a dealership location page for {dealer_name} ({url}).

Your task is to identify the HTML structure and suggest CSS selectors for extracting dealership data.
DO NOT extract the actual data - just identify the patterns.

IMPORTANT: Even if you're not 100% certain, make your best guess. A confidence of 0.5-0.7 is acceptable.
Only return confidence 0.0 if the page is clearly an error page or has NO dealership information at all.

Analyze the HTML and return a JSON object with this exact structure:
{{
  "strategy_type": "css_selectors",
  "container_selector": "CSS selector that identifies each dealership container (e.g., 'div.dealer-card', 'li.location', 'tr', 'div[class*=\"location\"]')",
  "name_selector": "CSS selector for dealership name (relative to container, e.g., 'h3', 'h2', 'a', '.name', 'strong')",
  "address_selector": "CSS selector for street address (or 'combined' if address is in one element)",
  "city_selector": "CSS selector for city (or 'combined' if part of address)",
  "state_selector": "CSS selector for state (or 'combined' if part of address)",
  "zip_selector": "CSS selector for ZIP code (or 'combined' if part of address)",
  "phone_selector": "CSS selector for phone number (e.g., 'a[href^=\"tel:\"]', '.phone', 'span[class*=\"phone\"]')",
  "website_selector": "CSS selector for website link (e.g., 'a.website', 'a[href*=\"http\"]')",
  "confidence": 0.75,
  "notes": "Brief notes about the structure"
}}

Look for:
1. Repeated container patterns - ANY repeating divs/lis/articles with similar structure
2. Common class names: location, dealer, store, card, listing, item, place, site, franchise
3. Common patterns: cards in a grid, list items, table rows
4. Links with dealership names
5. Address patterns (street, city, state, zip)
6. Phone numbers (tel: links or phone classes)

Tips:
- Use partial class matching: [class*="location"] instead of exact matches
- Look for semantic HTML: article, section, aside
- Check for data attributes: [data-location], [data-dealer]
- If addresses are combined, set city/state/zip to "combined"
- If you see ANY repeating pattern that might be dealerships, suggest it with confidence 0.6-0.8

Return ONLY valid JSON. No explanations before or after.

HTML sample:
{html}
"""
    
    def _parse_strategy_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse AI strategy response."""
        # Clean markdown formatting
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        response_text = response_text.strip()
        
        try:
            strategy = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['strategy_type', 'container_selector', 'confidence']
            if not all(field in strategy for field in required_fields):
                logger.warning(f"Strategy missing required fields: {strategy}")
                return None
            
            # Ensure confidence is a float between 0 and 1
            try:
                strategy['confidence'] = float(strategy.get('confidence', 0.0))
                strategy['confidence'] = max(0.0, min(1.0, strategy['confidence']))
            except (ValueError, TypeError):
                strategy['confidence'] = 0.5
            
            logger.debug(f"Parsed strategy: {strategy}")
            return strategy
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse strategy response as JSON: {e}")
            logger.debug(f"Response was: {response_text[:500]}")
            return None
    
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