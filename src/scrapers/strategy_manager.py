"""
Strategy manager for initializing and registering all scraping strategies.

This module handles the registration of all available scraping strategies
and provides a convenient way to get a fully configured scraper.
"""

import logging

from src.scrapers.scraper_registry import scraper_registry
from src.scrapers.strategies.json_ld_strategy import JsonLdStrategy
from src.scrapers.strategies.javascript_strategy import JavaScriptStrategy
from src.scrapers.strategies.lithia_strategy import LithiaStrategy
from src.scrapers.strategies.group1_automotive_strategy import Group1AutomotiveStrategy
from src.scrapers.strategies.autocanada_strategy import AutoCanadaStrategy
from src.scrapers.strategies.generic_dealer_strategy import GenericDealerStrategy
from src.scrapers.strategies.sonic_dealercom_strategy import DealerDotComLocationsStrategy
from src.scrapers.strategies.overfuel_locations_strategy import OverfuelLocationsStrategy
from src.scrapers.strategies.learned_rule_strategy import LearnedRuleExtractorStrategy
from src.scrapers.strategies.dealercom_content_blocks_strategy import DealerDotComContentBlocksStrategy
from src.scrapers.strategies.cooper_auto_strategy import CooperAutoStrategy
from src.scrapers.strategies.courtesy_automotive_strategy import CourtesyAutomotiveStrategy
from src.scrapers.strategies.ray_skillman_strategy import RaySkillmanStrategy
from src.scrapers.strategies.hudson_automotive_strategy import HudsonAutomotiveStrategy

logger = logging.getLogger(__name__)


def initialize_strategies() -> None:
    """Initialize and register all available scraping strategies."""
    
    # Register strategies (order matters - more specific strategies first)
    scraper_registry.register(CooperAutoStrategy())  # Domain-specific strategy
    scraper_registry.register(CourtesyAutomotiveStrategy())  # Domain-specific strategy
    scraper_registry.register(RaySkillmanStrategy())  # Domain-specific strategy
    scraper_registry.register(LithiaStrategy())
    scraper_registry.register(Group1AutomotiveStrategy())
    scraper_registry.register(AutoCanadaStrategy())
    scraper_registry.register(HudsonAutomotiveStrategy())  # Hudson-specific strategy
    scraper_registry.register(DealerDotComLocationsStrategy())
    scraper_registry.register(DealerDotComContentBlocksStrategy())
    scraper_registry.register(LearnedRuleExtractorStrategy())
    scraper_registry.register(OverfuelLocationsStrategy())
    scraper_registry.register(JsonLdStrategy())
    scraper_registry.register(JavaScriptStrategy())
    scraper_registry.register(GenericDealerStrategy())  # Most generic, try last
    
    logger.info(f"Initialized {len(scraper_registry.get_strategies())} scraping strategies")


def get_configured_scraper():
    """
    Get a scraper instance with all strategies registered.
    
    Returns:
        BaseScraper instance with all strategies loaded
    """
    # Initialize strategies if not already done
    if not scraper_registry.get_strategies():
        initialize_strategies()
    
    return scraper_registry.create_scraper()