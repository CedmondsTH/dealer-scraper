"""
Scraper registry for managing and organizing scraping strategies.

This module provides a centralized registry for all scraping strategies
and factory methods for creating scrapers.
"""

from typing import List, Optional
from .base_scraper import BaseScraper, ScraperStrategy


class ScraperRegistry:
    """Registry for managing scraping strategies."""
    
    def __init__(self):
        self._strategies: List[ScraperStrategy] = []
    
    def register(self, strategy: ScraperStrategy) -> None:
        """Register a new scraping strategy."""
        self._strategies.append(strategy)
        print(f"Registered scraper strategy: {strategy.strategy_name}")
    
    def get_strategies(self) -> List[ScraperStrategy]:
        """Get all registered strategies."""
        return self._strategies.copy()
    
    def create_scraper(self) -> BaseScraper:
        """Create a scraper with all registered strategies."""
        scraper = BaseScraper()
        for strategy in self._strategies:
            scraper.register_strategy(strategy)
        return scraper
    
    def find_strategy(self, name: str) -> Optional[ScraperStrategy]:
        """Find a strategy by name."""
        for strategy in self._strategies:
            if strategy.strategy_name.lower() == name.lower():
                return strategy
        return None
    
    def list_strategies(self) -> List[str]:
        """Get list of all strategy names."""
        return [strategy.strategy_name for strategy in self._strategies]


# Global registry instance
scraper_registry = ScraperRegistry()