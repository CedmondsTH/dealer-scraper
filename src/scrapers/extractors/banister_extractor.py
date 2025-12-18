"""
Banister-style dealer location extractor.

Extracts dealer data from location pages using panel-based card layouts
with h3 headers and paragraph elements for address/phone information.
"""
import re
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BanisterExtractor:
    """Extractor for Banister-style location pages with panel cards."""
    
    @property
    def extractor_name(self) -> str:
        return "Banister Style"
    
    def can_extract(self, soup: BeautifulSoup, page_url: str) -> bool:
        """Check if this page uses Banister-style panels."""
        dealer_panels = soup.find_all('div', class_=lambda x: x and 'panel' in x and 'panel-default' in x)
        return len(dealer_panels) > 0
    
    def extract(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from Banister-style location pages with panel cards."""
        dealers = []
        
        # Look for panel-based dealer cards
        dealer_panels = soup.find_all('div', class_=lambda x: x and 'panel' in x and 'panel-default' in x)
        logger.debug(f"BanisterExtractor found {len(dealer_panels)} panels")
        
        for panel in dealer_panels:
            dealer = self._extract_dealer_from_panel(panel, page_url)
            if dealer:
                dealers.append(dealer)
        
        return dealers
    
    def _extract_dealer_from_panel(self, panel: BeautifulSoup, page_url: str) -> Dict[str, Any] | None:
        """Extract dealer information from a single panel."""
        # Extract dealer name from h3/strong text
        name = self._extract_name(panel)
        if not name:
            logger.debug("Skipping panel - no name found")
            return None
        
        # Extract address and phone from paragraph elements
        street, city, state, zip_code, phone = self._extract_contact_info(panel)
        
        # If we got basic info, add the dealer
        logger.debug(f"Panel processed - name='{name}', street='{street}', city='{city}'")
        if name and street:
            logger.debug(f"Adding dealer: {name}")
            return {
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code,
                "phone": phone,
                "website": page_url
            }
        else:
            logger.debug("Skipping panel - missing name or street")
            return None
    
    def _extract_name(self, panel: BeautifulSoup) -> str:
        """Extract dealer name from panel."""
        name_el = panel.find('h3')
        if name_el:
            strong_el = name_el.find('strong')
            if strong_el:
                name = strong_el.get_text(strip=True).replace('\n', ' ').replace('\r', ' ')
                # Clean up extra spaces
                return ' '.join(name.split())
        return ""
    
    def _extract_contact_info(self, panel: BeautifulSoup) -> tuple[str, str, str, str, str]:
        """Extract address and phone from panel paragraphs."""
        street, city, state, zip_code, phone = "", "", "", "", ""
        
        # Get all paragraph elements
        p_elements = panel.find_all('p', class_='larger')
        logger.debug(f"Panel found {len(p_elements)} p.larger elements")
        
        # Address keywords for detection
        address_keywords = [
            'blvd', 'street', 'road', 'ave', 'dr', 'freeway', 'fwy', 'pkwy',
            'ste', 'suite', 'way', 'ln', 'lane', 'ct', 'court', 'pl', 'place',
            'hwy', 'st', 'rd', 'ave', 'drive', 'main', 'hill', 'kansas'
        ]
        
        for p in p_elements:
            # CRITICAL: Use get_text() with separator to preserve <br> as line breaks!
            p_text = p.get_text('\n', strip=True)
            logger.debug(f"p_text with line breaks: '{p_text}'")
            
            # Check if this paragraph contains a phone number
            phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', p_text)
            if phone_match:
                phone = phone_match.group(0)
                logger.debug(f"Found phone: {phone}")
                continue
            
            # Check if this paragraph contains an address
            if not phone_match and any(keyword in p_text.lower() for keyword in address_keywords):
                lines = [line.strip() for line in p_text.split('\n') if line.strip()]
                logger.debug(f"Address paragraph has {len(lines)} lines: {lines}")
                
                if len(lines) >= 2:
                    # First line is street
                    street = lines[0]
                    
                    # Second line is city, state, zip
                    city_line = lines[1]
                    city_match = re.match(r'([^,]+),?\s*([A-Z]{2})\s*(\d{5})', city_line)
                    if city_match:
                        city, state, zip_code = city_match.groups()
                        logger.debug(f"Parsed address - street='{street}', city='{city}', state='{state}'")
        
        return street, city, state, zip_code, phone

