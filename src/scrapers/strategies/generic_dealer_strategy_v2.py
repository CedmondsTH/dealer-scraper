"""
Refactored Generic Dealer Strategy - Modular version using extractors.

This strategy tries multiple extraction patterns to handle various dealer website formats.
Each extraction pattern is now a separate, focused extractor class for better maintainability.
"""
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import ScraperStrategy
from src.scrapers.extractors.banister_extractor import BanisterExtractor
from src.scrapers.extractors.heading_address_extractor import HeadingAddressExtractor
from src.scrapers.extractors.dealeron_extractor import DealerOnExtractor

logger = logging.getLogger(__name__)


class GenericDealerStrategyV2(ScraperStrategy):
    """
    Generic dealer scraping strategy that tries multiple extraction patterns.
    
    This refactored version uses modular extractors for better maintainability
    and testability. Each extractor handles a specific website pattern.
    """
    
    def __init__(self):
        """Initialize the strategy with all available extractors."""
        self.extractors = [
            BanisterExtractor(),
            DealerOnExtractor(),
            HeadingAddressExtractor(),
            # Add more extractors here as they're created
        ]
    
    @property
    def strategy_name(self) -> str:
        return "Generic Dealer HTML V2"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        """
        Generic strategy can handle any page as a fallback.
        Returns True to allow trying all extractors.
        """
        return True
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """
        Extract dealers from generic dealer HTML structures.
        
        Tries each registered extractor in sequence and combines results.
        """
        soup = BeautifulSoup(html, "html.parser")
        all_dealers = []
        
        for extractor in self.extractors:
            try:
                # Check if this extractor thinks it can handle this page
                if extractor.can_extract(soup, page_url):
                    dealers = extractor.extract(soup, page_url)
                    if dealers:
                        logger.debug(
                            f"{extractor.extractor_name} extraction found {len(dealers)} dealers"
                        )
                        all_dealers.extend(dealers)
            except Exception as e:
                logger.error(
                    f"{extractor.extractor_name} extraction failed: {e}",
                    exc_info=True
                )
                continue
        
        logger.debug(f"Generic dealer strategy V2 extracted {len(all_dealers)} dealers")
        return all_dealers

