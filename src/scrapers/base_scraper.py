"""
Base scraper classes and interfaces for dealer location extraction.

This module provides the foundation for implementing different
scraping strategies for various dealer website types.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag
import json
import re
import sys

from ..utils.address_parser import parse_address
from ..utils.data_cleaner import data_cleaner


class ScraperStrategy(ABC):
    """Abstract base class for scraping strategies."""
    
    @abstractmethod
    def can_handle(self, html: str, page_url: str) -> bool:
        """
        Determine if this strategy can handle the given page.
        
        Args:
            html: Page HTML content
            page_url: URL of the page
            
        Returns:
            True if this strategy can extract data from the page
        """
        pass
    
    @abstractmethod
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """
        Extract dealer data from the page.
        
        Args:
            html: Page HTML content  
            page_url: URL of the page
            
        Returns:
            List of dealer dictionaries with keys: name, street, city, state, zip, phone, website
        """
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Return a human-readable name for this strategy."""
        pass


class BaseScraper:
    """Base class providing common scraping utilities."""
    
    def __init__(self):
        self.strategies: List[ScraperStrategy] = []
    
    def register_strategy(self, strategy: ScraperStrategy) -> None:
        """Register a scraping strategy."""
        self.strategies.append(strategy)
    
    def extract_dealer_data(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """
        Extract dealer data using registered strategies.
        
        Args:
            html: Page HTML content
            page_url: URL of the page
            
        Returns:
            List of unique, validated dealer records
        """
        soup = BeautifulSoup(html, "html.parser")
        all_dealers = []
        
        # Try each strategy
        for strategy in self.strategies:
            try:
                if strategy.can_handle(html, page_url):
                    print(f"DEBUG: Using strategy: {strategy.strategy_name}", file=sys.stderr)
                    dealers = strategy.extract_dealers(html, page_url)
                    print(f"DEBUG: {strategy.strategy_name} found {len(dealers)} dealers", file=sys.stderr)
                    all_dealers.extend(dealers)
            except Exception as e:
                print(f"ERROR: Strategy {strategy.strategy_name} failed: {e}", file=sys.stderr)
                continue
        
        # Filter and deduplicate
        valid_dealers = [d for d in all_dealers if data_cleaner.is_valid_dealership(d)]
        print(f"Valid dealerships after filtering: {len(valid_dealers)}", file=sys.stderr)
        
        unique_dealers = data_cleaner.deduplicate_dealers(valid_dealers)
        print(f"Unique dealerships after deduplication: {len(unique_dealers)}", file=sys.stderr)
        
        return unique_dealers
    
    def create_dealer_record(self, name: str = "", street: str = "", city: str = "", 
                           state: str = "", zip_code: str = "", phone: str = "", 
                           website: str = "", page_url: str = "") -> Dict[str, Any]:
        """
        Create a standardized dealer record.
        
        Args:
            name: Dealer name
            street: Street address
            city: City name
            state: State/province code
            zip_code: Postal/ZIP code
            phone: Phone number
            website: Website URL
            page_url: Fallback URL if no website provided
            
        Returns:
            Standardized dealer dictionary
        """
        return {
            "name": name.strip() if name else "",
            "street": street.strip() if street else "",
            "city": city.strip() if city else "",
            "state": state.strip() if state else "",
            "zip": zip_code.strip() if zip_code else "",
            "phone": phone.strip() if phone else "",
            "website": website.strip() if website else page_url
        }
    
    def extract_text_safe(self, element: Optional[Tag], default: str = "") -> str:
        """Safely extract text from a BeautifulSoup element."""
        if element:
            return element.get_text(strip=True)
        return default
    
    def extract_href_safe(self, element: Optional[Tag], default: str = "") -> str:
        """Safely extract href attribute from a BeautifulSoup element."""
        if element and element.has_attr('href'):
            return element['href']
        return default
    
    def extract_attribute_safe(self, element: Optional[Tag], attr: str, default: str = "") -> str:
        """Safely extract any attribute from a BeautifulSoup element."""
        if element and element.has_attr(attr):
            return element[attr]
        return default
    
    def parse_address_components(self, address_text: str) -> Dict[str, str]:
        """
        Parse address text into components.
        
        Args:
            address_text: Raw address string
            
        Returns:
            Dictionary with keys: street, city, state, zip
        """
        street, city, state, zip_code = parse_address(address_text)
        return {
            "street": street,
            "city": city, 
            "state": state,
            "zip": zip_code
        }
    
    def find_phone_in_text(self, text: str) -> str:
        """Extract phone number from text using regex."""
        if not text:
            return ""
        
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group() if match else ""
    
    def make_absolute_url(self, url: str, base_url: str) -> str:
        """Convert relative URL to absolute URL."""
        if not url:
            return base_url
        
        if url.startswith('http'):
            return url
        
        if url.startswith('/'):
            # Get base domain
            parts = base_url.split('/')
            if len(parts) >= 3:
                base = f"{parts[0]}//{parts[2]}"
                return base + url
        else:
            # Relative path
            return base_url.rstrip('/') + '/' + url.lstrip('/')
        
        return url