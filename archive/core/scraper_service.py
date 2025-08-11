"""
Main scraper service providing high-level scraping operations.

This service coordinates web scraping, data extraction, and processing
operations with proper error handling and logging.
"""

import logging
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from scrapers.strategy_manager import get_configured_scraper
from .web_scraper import WebScraper
from .data_service import DataService


class ScrapingStatus(Enum):
    """Status codes for scraping operations."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    NO_DATA = "no_data"


@dataclass
class ScrapingResult:
    """Result of a scraping operation."""
    status: ScrapingStatus
    dealers: List[Dict[str, Any]]
    message: str
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.status in (ScrapingStatus.SUCCESS, ScrapingStatus.PARTIAL_SUCCESS)


class ScraperService:
    """High-level service for dealer scraping operations."""
    
    def __init__(self, web_scraper: Optional[WebScraper] = None, 
                 data_service: Optional[DataService] = None):
        self.logger = logging.getLogger(__name__)
        self.web_scraper = web_scraper or WebScraper()
        self.data_service = data_service or DataService()
        self.extractor = get_configured_scraper()
    
    def scrape_dealer_locations(self, dealer_name: str, url: str) -> ScrapingResult:
        """
        Scrape dealer locations from a given URL.
        
        Args:
            dealer_name: Name of the dealer group
            url: URL to scrape
            
        Returns:
            ScrapingResult with status and extracted data
        """
        try:
            self.logger.info(f"Starting scrape for {dealer_name} at {url}")
            
            # Step 1: Fetch web page content
            html_content = self.web_scraper.fetch_page(url)
            if not html_content:
                return ScrapingResult(
                    status=ScrapingStatus.FAILED,
                    dealers=[],
                    message="Failed to fetch page content",
                    error="Empty or invalid response from website"
                )
            
            # Step 2: Extract dealer data
            raw_dealers = self.extractor.extract_dealer_data(html_content, url)
            
            # Step 3: Process and validate data
            processed_dealers = self.data_service.process_dealer_data(
                raw_dealers, dealer_name
            )
            
            # Step 4: Determine result status
            if not processed_dealers:
                return ScrapingResult(
                    status=ScrapingStatus.NO_DATA,
                    dealers=[],
                    message="No valid dealer locations found"
                )
            
            success_status = (ScrapingStatus.SUCCESS if len(processed_dealers) >= len(raw_dealers) * 0.8
                            else ScrapingStatus.PARTIAL_SUCCESS)
            
            self.logger.info(f"Scraping completed: {len(processed_dealers)} dealers extracted")
            
            return ScrapingResult(
                status=success_status,
                dealers=processed_dealers,
                message=f"Successfully extracted {len(processed_dealers)} dealer locations"
            )
            
        except Exception as e:
            self.logger.error(f"Scraping failed for {dealer_name}: {str(e)}", exc_info=True)
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                dealers=[],
                message="Scraping operation failed",
                error=str(e)
            )
    
    def scrape_multiple_urls(self, dealer_name: str, urls: List[str]) -> ScrapingResult:
        """
        Scrape multiple URLs for a dealer group.
        
        Args:
            dealer_name: Name of the dealer group
            urls: List of URLs to scrape
            
        Returns:
            Combined ScrapingResult from all URLs
        """
        all_dealers = []
        errors = []
        
        for url in urls:
            result = self.scrape_dealer_locations(dealer_name, url)
            if result.success:
                all_dealers.extend(result.dealers)
            elif result.error:
                errors.append(f"{url}: {result.error}")
        
        # Deduplicate across all URLs
        unique_dealers = self.data_service.deduplicate_dealers(all_dealers)
        
        if not unique_dealers:
            return ScrapingResult(
                status=ScrapingStatus.NO_DATA,
                dealers=[],
                message="No valid dealers found across all URLs",
                error="; ".join(errors) if errors else None
            )
        
        return ScrapingResult(
            status=ScrapingStatus.SUCCESS,
            dealers=unique_dealers,
            message=f"Successfully extracted {len(unique_dealers)} unique dealers from {len(urls)} URLs"
        )