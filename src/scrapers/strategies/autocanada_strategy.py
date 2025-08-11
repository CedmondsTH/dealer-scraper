"""
AutoCanada specific scraping strategy.

This strategy handles the HTML structure used by
AutoCanada dealer location pages.
"""

from typing import List, Dict, Any
import re
import sys
from bs4 import BeautifulSoup

from ..base_scraper import ScraperStrategy
from ...utils.address_parser import parse_address


class AutoCanadaStrategy(ScraperStrategy):
    """Extracts dealer data from AutoCanada HTML structure."""
    
    @property
    def strategy_name(self) -> str:
        return "AutoCanada HTML"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if page contains AutoCanada structure."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Look for AutoCanada specific elements
        cards = soup.select("div.well.matchable-heights")
        if not cards:
            return False
        
        # Check for AutoCanada specific elements within cards
        sample_card = cards[0]
        has_dealer_address = sample_card.select_one("span.di-dealer-address")
        has_dealer_phone = sample_card.select_one("span.dealer-phone")
        
        return has_dealer_address and has_dealer_phone
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealers from AutoCanada HTML structure."""
        soup = BeautifulSoup(html, "html.parser")
        dealers = []
        
        canadian_provinces = {"AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"}
        
        for card in soup.select("div.well.matchable-heights"):
            dealer = self._extract_dealer_from_card(card, page_url, canadian_provinces)
            if dealer:
                dealers.append(dealer)
        
        print(f"DEBUG: AutoCanada strategy extracted {len(dealers)} dealers", file=sys.stderr)
        return dealers
    
    def _extract_dealer_from_card(self, card, page_url: str, canadian_provinces: set) -> Dict[str, Any]:
        """Extract dealer information from an AutoCanada card element."""
        try:
            # Extract dealer name
            name_el = card.select_one("h2")
            name = name_el.get_text(strip=True) if name_el else ""
            
            if not name:
                return None
            
            # Extract website
            website = page_url
            if name_el:
                parent_a = name_el.find_parent("a")
                if parent_a and parent_a.has_attr("href"):
                    website = parent_a["href"]
            
            # Extract address
            address_el = card.select_one("span.di-dealer-address")
            address_html = address_el.decode_contents() if address_el else ""
            
            # Split address on <br> or newlines
            parts = re.split(r'<br\s*/?>|\n', address_html)
            parts = [BeautifulSoup(p, 'html.parser').get_text(" ", strip=True) for p in parts if p.strip()]
            address_text = ", ".join(parts)
            
            # Parse address
            street, city, state, zip_code = parse_address(address_text)
            
            # Set country based on province
            if not state and city in canadian_provinces:
                state = "Canada"
            elif not state:
                state = "United States of America"
            
            # Extract phone
            phone_el = card.select_one("span.dealer-phone.sales span")
            phone = phone_el.get_text(strip=True) if phone_el else ""
            
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
            print(f"DEBUG: Error extracting dealer from AutoCanada card: {e}", file=sys.stderr)
            return None