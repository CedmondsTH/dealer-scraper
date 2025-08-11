"""
Lithia Motors specific scraping strategy.

This strategy handles the specific HTML structure used by
Lithia Motors dealer location pages.
"""

from typing import List, Dict, Any
import sys
from bs4 import BeautifulSoup

from ..base_scraper import ScraperStrategy


class LithiaStrategy(ScraperStrategy):
    """Extracts dealer data from Lithia Motors specific HTML structure."""
    
    @property
    def strategy_name(self) -> str:
        return "Lithia Motors HTML"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if page contains Lithia-specific HTML structure."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Look for Lithia-specific CSS classes
        lithia_indicators = soup.select("li.info-window")
        
        # Also check for Lithia in the page content or URL
        is_lithia_page = (
            "lithia" in page_url.lower() or
            "lithia" in html.lower()
        )
        
        return len(lithia_indicators) > 0 and is_lithia_page
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from Lithia-specific HTML structure."""
        soup = BeautifulSoup(html, "html.parser")
        dealers = []
        
        # Extract from li.info-window elements
        for li in soup.select("li.info-window"):
            dealer = self._extract_dealer_from_info_window(li, page_url)
            if dealer:
                dealers.append(dealer)
        
        print(f"DEBUG: Lithia strategy extracted {len(dealers)} dealers", file=sys.stderr)
        return dealers
    
    def _extract_dealer_from_info_window(self, li_element, page_url: str) -> Dict[str, Any]:
        """Extract dealer information from a Lithia info-window element."""
        try:
            # Extract dealer name
            name_el = li_element.select_one(".org")
            name = name_el.get_text(strip=True) if name_el else ""
            
            if not name:
                return None
            
            # Extract website
            website_el = li_element.select_one("a.url")
            website = ""
            if website_el and website_el.has_attr("href"):
                website = website_el["href"]
            else:
                website = page_url
            
            # Extract address components
            street_el = li_element.select_one(".street-address")
            city_el = li_element.select_one(".locality")
            state_el = li_element.select_one(".region")
            zip_el = li_element.select_one(".postal-code")
            
            street = street_el.get_text(strip=True) if street_el else ""
            city = city_el.get_text(strip=True) if city_el else ""
            state = state_el.get_text(strip=True) if state_el else ""
            zip_code = zip_el.get_text(strip=True) if zip_el else ""
            
            # Extract phone number
            phone = ""
            phone_el = li_element.select_one(".tel[data-click-to-call='Sales']")
            
            if phone_el and phone_el.has_attr("data-click-to-call-phone"):
                phone = phone_el["data-click-to-call-phone"]
            else:
                phone_val = li_element.select_one(".tel[data-click-to-call='Sales'] .value")
                if phone_val:
                    phone = phone_val.get_text(strip=True)
            
            return {
                "name": name,
                "street": street,
                "city": city,
                "state": state,
                "zip": zip_code,
                "phone": phone,
                "website": website
            }
            
        except Exception as e:
            print(f"DEBUG: Error extracting dealer from Lithia info-window: {e}", file=sys.stderr)
            return None