"""
Smart generic scraper that uses AI-suggested strategies.

This scraper combines AI intelligence (for identifying patterns) with
traditional code execution (for reliable, fast extraction).
"""

import re
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup, Tag

from scrapers.base import BaseScraper
from scrapers.ai_fallback import AIFallbackScraper
from models.dealership import DealershipData
from utils.strategy_cache import strategy_cache
from utils.logging import logger


class SmartGenericScraper(BaseScraper):
    """
    Generic scraper that uses AI to identify extraction strategies.
    
    Flow:
    1. Check cache for known strategy
    2. If not cached, use AI to analyze structure
    3. Execute strategy using traditional CSS selectors
    4. Cache successful strategies for future use
    """
    
    def __init__(self):
        super().__init__("Smart Generic (AI-Guided)")
        self.ai_analyzer = AIFallbackScraper()
        self.min_confidence = 0.5  # Minimum confidence to try a strategy (lowered to be more permissive)
    
    def can_handle(self, html: str, url: str) -> bool:
        """
        Can handle any site if AI is available or strategy is cached.
        """
        # Can handle if we have a cached strategy OR AI is available
        return (strategy_cache.get_strategy(url) is not None or 
                self.ai_analyzer.model is not None)
    
    def extract(self, html: str, url: str) -> List[DealershipData]:
        """Extract dealerships using AI-guided strategy."""
        soup = self._get_soup(html)
        
        # Step 1: Try to get cached strategy
        strategy = strategy_cache.get_strategy(url)
        
        if strategy:
            logger.info(f"{self.name}: Using cached strategy for {url}")
            cached_strategy = strategy.get('strategy', {})
        else:
            # Step 2: Use AI to analyze structure
            logger.info(f"{self.name}: Analyzing structure with AI for {url}")
            cached_strategy = self.ai_analyzer.analyze_structure(html, url)
            
            if not cached_strategy:
                logger.warning(f"{self.name}: AI could not determine strategy")
                return []
            
            # Check confidence threshold
            confidence = cached_strategy.get('confidence', 0.0)
            if confidence < self.min_confidence:
                logger.warning(f"{self.name}: Strategy confidence too low "
                             f"({confidence:.2f} < {self.min_confidence})")
                return []
        
        # Step 3: Execute the strategy
        logger.info(f"{self.name}: Executing strategy "
                   f"(type: {cached_strategy.get('strategy_type')})")
        dealerships = self._execute_strategy(soup, cached_strategy, url)
        
        # Step 4: Cache strategy if successful
        if dealerships:
            logger.info(f"{self.name}: Successfully extracted {len(dealerships)} "
                       f"dealerships using AI-guided strategy")
            strategy_cache.save_strategy(url, cached_strategy, success=True)
        else:
            logger.warning(f"{self.name}: Strategy extracted 0 dealerships")
            strategy_cache.save_strategy(url, cached_strategy, success=False)
        
        return dealerships
    
    def _execute_strategy(self, soup: BeautifulSoup, strategy: Dict[str, Any], 
                          url: str) -> List[DealershipData]:
        """
        Execute an extraction strategy.
        
        Args:
            soup: Parsed HTML
            strategy: Strategy dictionary from AI
            url: Page URL
            
        Returns:
            List of extracted dealerships
        """
        strategy_type = strategy.get('strategy_type', 'css_selectors')
        
        if strategy_type == 'css_selectors':
            return self._execute_css_strategy(soup, strategy, url)
        else:
            logger.warning(f"Unknown strategy type: {strategy_type}")
            return []
    
    def _execute_css_strategy(self, soup: BeautifulSoup, strategy: Dict[str, Any],
                               url: str) -> List[DealershipData]:
        """
        Execute CSS selector-based extraction strategy.
        
        Args:
            soup: Parsed HTML
            strategy: Strategy with CSS selectors
            url: Page URL
            
        Returns:
            List of extracted dealerships
        """
        dealerships = []
        
        # Get container selector
        container_selector = strategy.get('container_selector', '')
        if not container_selector:
            logger.warning("No container selector in strategy")
            return []
        
        # Find all containers
        try:
            containers = soup.select(container_selector)
            logger.debug(f"Found {len(containers)} containers with selector: {container_selector}")
        except Exception as e:
            logger.error(f"Invalid container selector '{container_selector}': {e}")
            return []
        
        if not containers:
            logger.warning(f"No containers found with selector: {container_selector}")
            return []
        
        # Extract data from each container
        for i, container in enumerate(containers):
            try:
                dealership = self._extract_from_container(container, strategy, url)
                if dealership and dealership.name:  # Only add if we got at least a name
                    dealerships.append(dealership)
                    logger.debug(f"Extracted dealership {i+1}: {dealership.name}")
            except Exception as e:
                logger.warning(f"Failed to extract from container {i+1}: {e}")
                continue
        
        return dealerships
    
    def _extract_from_container(self, container: Tag, strategy: Dict[str, Any],
                                 url: str) -> Optional[DealershipData]:
        """
        Extract dealership data from a single container element.
        
        Args:
            container: Container element
            strategy: Strategy with selectors
            url: Page URL
            
        Returns:
            DealershipData or None
        """
        # Extract fields using selectors
        name = self._extract_field(container, strategy.get('name_selector'))
        phone = self._extract_field(container, strategy.get('phone_selector'))
        website = self._extract_field(container, strategy.get('website_selector'), 
                                      attr='href', base_url=url)
        
        # Handle address extraction (may be combined or separate)
        address_selector = strategy.get('address_selector', '')
        city_selector = strategy.get('city_selector', '')
        state_selector = strategy.get('state_selector', '')
        zip_selector = strategy.get('zip_selector', '')
        
        # Check if address components are combined
        if (city_selector == 'combined' or state_selector == 'combined' or 
            zip_selector == 'combined'):
            # Address is in one element, need to parse it
            full_address = self._extract_field(container, address_selector)
            street, city, state, zip_code = self._parse_combined_address(full_address)
        else:
            # Address components are separate
            street = self._extract_field(container, address_selector)
            city = self._extract_field(container, city_selector)
            state = self._extract_field(container, state_selector)
            zip_code = self._extract_field(container, zip_selector)
        
        # Create dealership object
        dealership = DealershipData(
            name=name,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone,
            website=website
        )
        
        return dealership
    
    def _extract_field(self, container: Tag, selector: Optional[str], 
                       attr: Optional[str] = None, base_url: Optional[str] = None) -> str:
        """
        Extract a single field from container using selector.
        
        Args:
            container: Container element
            selector: CSS selector (relative to container)
            attr: Attribute to extract (e.g., 'href') instead of text
            base_url: Base URL for resolving relative URLs
            
        Returns:
            Extracted text or empty string
        """
        if not selector or selector == 'combined':
            return ""
        
        try:
            element = container.select_one(selector)
            if not element:
                return ""
            
            if attr:
                value = element.get(attr, '')
                if value and base_url:
                    value = self._resolve_url(value, base_url)
                return str(value).strip()
            else:
                return element.get_text(strip=True)
        except Exception as e:
            logger.debug(f"Failed to extract field with selector '{selector}': {e}")
            return ""
    
    def _resolve_url(self, url: str, base_url: str) -> str:
        """Resolve relative URL to absolute."""
        from urllib.parse import urljoin, urlparse
        
        # If it's already absolute, return as is
        if urlparse(url).netloc:
            return url
        
        # Otherwise resolve relative to base
        return urljoin(base_url, url)
    
    def _parse_combined_address(self, address: str) -> tuple:
        """
        Parse combined address into components.
        
        Handles formats like:
        - "123 Main St, Springfield, IL 62701"
        - "456 Oak Ave, Suite 100, Denver, CO 80202"
        
        Returns:
            Tuple of (street, city, state, zip_code)
        """
        if not address:
            return ("", "", "", "")
        
        # Try common pattern: Street, City, ST ZIP
        # Using a regex that handles optional suite/unit numbers
        pattern = r'^(.+?),\s*([^,]+?),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)$'
        match = re.match(pattern, address)
        
        if match:
            street = match.group(1).strip()
            city = match.group(2).strip()
            state = match.group(3).strip()
            zip_code = match.group(4).strip()
            return (street, city, state, zip_code)
        
        # If pattern doesn't match, try simpler split
        parts = [p.strip() for p in address.split(',')]
        
        if len(parts) >= 3:
            # Assume: street, city, state+zip
            street = parts[0]
            city = parts[1] if len(parts) > 1 else ""
            
            # Try to parse state and zip from last part
            last_part = parts[-1]
            state_zip_match = re.search(r'([A-Z]{2})\s*(\d{5}(?:-\d{4})?)', last_part)
            if state_zip_match:
                state = state_zip_match.group(1)
                zip_code = state_zip_match.group(2)
            else:
                state = last_part
                zip_code = ""
            
            return (street, city, state, zip_code)
        
        # Fallback: put everything in street
        return (address, "", "", "")

