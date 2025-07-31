"""
Group 1 Automotive specific scraping strategy.

This module handles extraction from Group 1 Automotive dealership websites
using their specific card-based layout patterns.
"""

import re
from typing import List
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from models.dealership import DealershipData
from utils.parsers import parse_address


class Group1Scraper(BaseScraper):
    """Scraper for Group 1 Automotive dealership websites."""
    
    def __init__(self):
        super().__init__("Group 1 Automotive")
    
    def can_handle(self, html: str, url: str) -> bool:
        """Check if this is a Group 1 Automotive website."""
        return (
            "group1auto" in url.lower() or
            "div.dealer-card" in html or
            "div.g1-location-card" in html
        )
    
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """Extract dealership data from Group 1 Automotive website."""
        soup = self._get_soup(html)
        dealerships = []
        
        # Group 1-specific patterns
        patterns = [
            "div.dealer-card",
            "div.location-card", 
            "div.g1-location-card",
            "div.location.dealer"
        ]
        
        for pattern in patterns:
            cards = soup.select(pattern)
            if cards:
                for card in cards:
                    if pattern == "div.location.dealer":
                        dealership = self._extract_from_subpage_card(card, url)
                    else:
                        dealership = self._extract_from_main_card(card, url)
                    if dealership:
                        dealerships.append(dealership)
                
                if dealerships:
                    self.logger.pattern_success(f"{self.name} - {pattern}", len(dealerships))
                    break
        
        return dealerships
    
    def _extract_from_main_card(self, card, url: str) -> DealershipData:
        """Extract from main page dealer cards."""
        name_el = card.select_one(".dealer-title, .dealer-name, h2, h3, h4")
        address_el = card.select_one(".dealer-address, .address, address, .dealer-info__address")
        phone_el = card.select_one(".dealer-phone, .phone, a[href^='tel:'], .dealer-info__phone")
        
        # Look for website link (exclude group1auto.com links)
        website_el = card.select_one("a[href^='http']:not([href*='group1auto.com'])")
        if not website_el:
            website_el = card.select_one("a.btn, a.button, a[role='button']")
        
        name = self._extract_text_safely(name_el)
        address = self._extract_text_safely(address_el, separator=", ")
        phone = self._extract_text_safely(phone_el)
        website = self._extract_attribute_safely(website_el, "href", url)
        
        # Parse address into components
        street, city, state, zip_code = self._parse_group1_address(address)
        
        if name or street:
            return DealershipData(
                name=name,
                street=street,
                city=city,
                state=state,
                zip_code=zip_code,
                phone=phone,
                website=website
            )
        return None
    
    def _extract_from_subpage_card(self, card, url: str) -> DealershipData:
        """Extract from subpage dealer cards."""
        name_el = card.select_one("h3.af-brand-text")
        p_tags = card.find_all("p")
        
        street = self._extract_text_safely(p_tags[0]) if len(p_tags) > 0 else ""
        city, state, zip_code = "", "", ""
        
        if len(p_tags) > 1:
            city_state_zip = self._extract_text_safely(p_tags[1])
            m = re.match(r"([\w\s\.-]+),\s*([A-Z]{2})\s*(\d{5})", city_state_zip)
            if m:
                city = m.group(1).strip()
                state = m.group(2)
                zip_code = m.group(3)
        
        phone = self._extract_text_safely(p_tags[2]) if len(p_tags) > 2 else ""
        
        # Look for website
        website = url
        for a in card.select("a"):
            if self._extract_text_safely(a).lower() == "website" and a.has_attr("href"):
                website = a["href"]
                break
        
        return DealershipData(
            name=self._extract_text_safely(name_el),
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone,
            website=website
        )
    
    def _parse_group1_address(self, address: str) -> tuple:
        """Parse Group 1 specific address format."""
        # Try regex pattern first
        m = re.match(r"(.+),\s*([\w\s\.-]+),\s*([A-Z]{2})\s*(\d{5})", address)
        if m:
            return m.group(1).strip(), m.group(2).strip(), m.group(3), m.group(4)
        
        # Fallback to comma splitting
        parts = address.split(",")
        if len(parts) >= 3:
            street = parts[0].strip()
            city = parts[1].strip()
            state_zip = parts[2].strip().split()
            if len(state_zip) == 2:
                state, zip_code = state_zip
                return street, city, state, zip_code
        
        # Use general parser as last resort
        return parse_address(address)