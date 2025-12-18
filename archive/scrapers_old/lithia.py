"""
Lithia Motors specific scraping strategy.

This module handles extraction from Lithia Motors dealership websites
using their specific HTML structure and microdata patterns.
"""

from typing import List
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from models.dealership import DealershipData
from utils.parsers import parse_address


class LithiaScraper(BaseScraper):
    """Scraper for Lithia Motors dealership websites."""
    
    def __init__(self):
        super().__init__("Lithia Motors")
    
    def can_handle(self, html: str, url: str) -> bool:
        """Check if this is a Lithia Motors website."""
        return (
            "lithia" in url.lower() or
            "li.info-window" in html or
            "Lithia" in html
        )
    
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """Extract dealership data from Lithia Motors website."""
        soup = self._get_soup(html)
        dealerships = []
        
        # Lithia-specific pattern: li.info-window
        for li in soup.select("li.info-window"):
            dealership = self._extract_from_info_window(li, url)
            if dealership:
                dealerships.append(dealership)
        
        if dealerships:
            self.logger.pattern_success(self.name, len(dealerships))
        
        return dealerships
    
    def _extract_from_info_window(self, li, url: str) -> DealershipData:
        """Extract dealership data from info-window element."""
        name_el = li.select_one(".org")
        website_el = li.select_one("a.url")
        street_el = li.select_one(".street-address")
        city_el = li.select_one(".locality")
        state_el = li.select_one(".region")
        zip_el = li.select_one(".postal-code")
        
        # Handle phone extraction
        phone_el = li.select_one(".tel[data-click-to-call='Sales']")
        phone_val = li.select_one(".tel[data-click-to-call='Sales'] .value")
        
        phone = ""
        if phone_el and phone_el.has_attr("data-click-to-call-phone"):
            phone = phone_el["data-click-to-call-phone"]
        elif phone_val:
            phone = self._extract_text_safely(phone_val)
        
        return DealershipData(
            name=self._extract_text_safely(name_el),
            street=self._extract_text_safely(street_el),
            city=self._extract_text_safely(city_el),
            state=self._extract_text_safely(state_el),
            zip_code=self._extract_text_safely(zip_el),
            phone=phone,
            website=self._extract_attribute_safely(website_el, "href", url)
        )