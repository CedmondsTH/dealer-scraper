"""
Base scraper functionality and interfaces.

This module provides the foundation for all scraping strategies
with common functionality and standardized interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from models.dealership import DealershipData
from utils.logging import logger


class BaseScraper(ABC):
    """Abstract base class for all scraping strategies."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger
    
    @abstractmethod
    def can_handle(self, html: str, url: str) -> bool:
        """
        Check if this scraper can handle the given website.
        
        Args:
            html: Website HTML content
            url: Website URL
            
        Returns:
            True if this scraper can handle the website
        """
        pass
    
    @abstractmethod
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """
        Extract dealership data from the website.
        
        Args:
            html: Website HTML content
            url: Website URL
            
        Returns:
            List of extracted dealership data
        """
        pass
    
    def _get_soup(self, html: str) -> BeautifulSoup:
        """Create BeautifulSoup object from HTML."""
        return BeautifulSoup(html, "html.parser")
    
    def _extract_text_safely(self, element, default: str = "") -> str:
        """Safely extract text from BeautifulSoup element."""
        if element is None:
            return default
        return element.get_text(strip=True)
    
    def _extract_attribute_safely(self, element, attribute: str, default: str = "") -> str:
        """Safely extract attribute from BeautifulSoup element."""
        if element is None or not element.has_attr(attribute):
            return default
        return element[attribute]


class GenericScraper(BaseScraper):
    """Generic scraper that tries multiple common patterns."""
    
    def __init__(self):
        super().__init__("Generic")
    
    def can_handle(self, html: str, url: str) -> bool:
        """Generic scraper can handle any website as fallback."""
        return True
    
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """Extract using multiple generic patterns."""
        soup = self._get_soup(html)
        dealerships = []
        
        # Try common dealership card patterns
        patterns = [
            "div.dealer-card",
            "div.location-card", 
            "div.dealership",
            "div.location",
            ".dealer-info",
            ".location-info"
        ]
        
        for pattern in patterns:
            cards = soup.select(pattern)
            if cards:
                self.logger.debug(f"Found {len(cards)} elements with pattern: {pattern}")
                for card in cards:
                    dealership = self._extract_from_card(card, url)
                    if dealership and dealership.name and dealership.street:
                        dealerships.append(dealership)
                        
                if dealerships:
                    break  # Stop at first successful pattern
        
        return dealerships
    
    def _extract_from_card(self, card, url: str) -> Optional[DealershipData]:
        """Extract dealership data from a card element."""
        # Try various selectors for name
        name_selectors = ["h1", "h2", "h3", "h4", ".name", ".title", ".dealer-name"]
        name = ""
        for selector in name_selectors:
            name_el = card.select_one(selector)
            if name_el:
                name = self._extract_text_safely(name_el)
                break
        
        # Try various selectors for address
        address_selectors = [".address", ".location", ".street", "address"]
        address = ""
        for selector in address_selectors:
            addr_el = card.select_one(selector)
            if addr_el:
                address = self._extract_text_safely(addr_el)
                break
        
        # Try to find phone
        phone_selectors = [".phone", "a[href^='tel:']", ".contact"]
        phone = ""
        for selector in phone_selectors:
            phone_el = card.select_one(selector)
            if phone_el:
                phone = self._extract_text_safely(phone_el)
                break
        
        # Try to find website
        website_selectors = ["a[href^='http']", ".website", ".url"]
        website = url  # Default to page URL
        for selector in website_selectors:
            web_el = card.select_one(selector)
            if web_el:
                website = self._extract_attribute_safely(web_el, "href", url)
                break
        
        if not name or not address:
            return None
        
        return DealershipData(
            name=name,
            street=address,
            phone=phone,
            website=website
        )