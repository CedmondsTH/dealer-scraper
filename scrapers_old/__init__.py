"""
Scraper modules for dealership data extraction.

This package contains all scraping strategies for different
dealership group websites and patterns.
"""

from typing import List
from scrapers.base import BaseScraper, GenericScraper
from scrapers.lithia import LithiaScraper
from scrapers.group1 import Group1Scraper
from scrapers.edwards import EdwardsScraper
from scrapers.kenganley import KenGanleyScraper
from scrapers.sonic import SonicScraper
from scrapers.smart_generic import SmartGenericScraper
from scrapers.ai_fallback import AIFallbackScraper


class ScraperManager:
    """Manages and coordinates all scraping strategies."""
    
    def __init__(self):
        # Initialize all scrapers in priority order
        self.scrapers = [
            # Specific dealer group scrapers (fast, reliable, free)
            LithiaScraper(),
            Group1Scraper(),
            EdwardsScraper(),  # Edwards Auto Group specific
            KenGanleyScraper(), # Ken Ganley specific
            SonicScraper(),  # Sonic Automotive specific
            # Add more specific scrapers here
            
            # AI extraction (works on most sites, small cost ~$0.02 per scrape)
            AIFallbackScraper(),  # Direct AI extraction - reliable for unknown sites
            
            # Pattern-based fallbacks (free but less reliable)
            SmartGenericScraper(),  # Uses AI to identify extraction strategy
            GenericScraper(),  # Basic generic patterns (last resort)
        ]
    
    def extract_dealerships(self, html: str, url: str, dealer_name: str = "") -> List:
        """
        Extract dealerships using the most appropriate scraper.
        
        Args:
            html: Website HTML content
            url: Website URL
            dealer_name: Optional dealer group name
            
        Returns:
            List of DealershipData objects
        """
        from models.dealership import DealershipCollection
        from utils.logging import logger
        
        collection = DealershipCollection()
        
        # Try each scraper in order until one succeeds
        for scraper in self.scrapers:
            if scraper.can_handle(html, url):
                logger.debug(f"Trying scraper: {scraper.name}")
                
                try:
                    dealerships = scraper.extract(html, url)
                    
                    # Set dealer group name
                    for dealership in dealerships:
                        if dealer_name and not dealership.dealer_group:
                            dealership.dealer_group = dealer_name
                    
                    collection.extend(dealerships)
                    
                    # If we found dealerships, we're done
                    if dealerships:
                        logger.info(f"Successfully extracted {len(collection)} dealerships using {scraper.name}")
                        break
                    
                except Exception as e:
                    logger.error(f"Scraper {scraper.name} failed: {e}")
                    continue
        
        return list(collection)


# Global scraper manager instance
scraper_manager = ScraperManager()