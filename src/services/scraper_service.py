"""
Main scraper service providing high-level scraping operations.

This service coordinates web scraping, data extraction, and processing
operations with proper error handling and logging.
"""

import logging
import sys
from typing import List, Dict, Any, Optional
import re
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum

from ..scrapers.strategy_manager import get_configured_scraper
from .web_scraper import WebScraper
from .data_service import DataService
from ..scrapers.strategies.new_llm_strategy import NewLLMExtractorStrategy


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
        self.llm_fallback = NewLLMExtractorStrategy()
    
    def scrape_dealer_locations(self, dealer_name: str, url: str, progress_callback=None) -> ScrapingResult:
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
            if progress_callback:
                progress_callback(25, "Fetching page content...")
            html_content = self.web_scraper.fetch_page(url)
            if not html_content:
                return ScrapingResult(
                    status=ScrapingStatus.FAILED,
                    dealers=[],
                    message="Failed to fetch page content",
                    error="Empty or invalid response from website"
                )
            
            # Step 2: Extract dealer data
            if progress_callback:
                progress_callback(50, "Analyzing website structure...")
            raw_dealers = self.extractor.extract_dealer_data(html_content, url)
            
            # Step 3: Process and validate data
            if progress_callback:
                progress_callback(60, "Processing dealer data...")
            processed_dealers = self.data_service.process_dealer_data(
                raw_dealers, dealer_name
            )

            # Automatic retry: if no dealers found, attempt force Playwright and re-extract
            if not processed_dealers:
                if progress_callback:
                    progress_callback(70, "No dealers found, trying enhanced scraping...")
                self.logger.info("No dealers after first pass; retrying with forced Playwright fetch...")
                html_content_retry = self.web_scraper.fetch_page(url, force_playwright=True)
                if html_content_retry:
                    raw_dealers_retry = self.extractor.extract_dealer_data(html_content_retry, url)
                    processed_dealers = self.data_service.process_dealer_data(
                        raw_dealers_retry, dealer_name
                    )
            
            # Step 4: Determine result status
            if not processed_dealers:
                # Try LLM fallback extraction as a last resort
                try:
                    if progress_callback:
                        progress_callback(80, "🤖 Using AI to extract dealer information...")
                    self.logger.info("No dealers found after retries; attempting LLM fallback extractor...")
                    dealers_llm = self.llm_fallback._extract_with_llm(html_content_retry or html_content, url)
                    if dealers_llm:
                        self.logger.info(f"LLM fallback extracted {len(dealers_llm)} dealers")
                        processed_dealers = self.data_service.process_dealer_data(dealers_llm, dealer_name)
                        # Return immediately if LLM found dealers
                        if processed_dealers:
                            if progress_callback:
                                progress_callback(100, f"✅ AI successfully extracted {len(processed_dealers)} dealers!")
                            return ScrapingResult(
                                status=ScrapingStatus.SUCCESS,
                                dealers=processed_dealers,
                                message=f"Successfully extracted {len(processed_dealers)} dealer locations via LLM"
                            )
                    else:
                        self.logger.warning("LLM fallback returned no dealers")
                except Exception as e:
                    self.logger.error(f"LLM fallback failed: {str(e)}")
                    import traceback
                    self.logger.error(f"LLM fallback traceback: {traceback.format_exc()}")

                # Generic fallback: try sitemap crawl for "locations" directories that are JS-rendered
                parsed = urlparse(url)
                hostname = (parsed.hostname or "").lower()
                path = (parsed.path or "").lower()
                if any(k in path for k in ("/locations", "locations.", "our-locations", "/location/")):
                    self.logger.info("No dealers found; attempting sitemap crawl for locations pages...")
                    sitemap_dealers = self._crawl_sitemap_locations(url, dealer_name)
                    if sitemap_dealers:
                        self.logger.info(f"Sitemap crawl recovered {len(sitemap_dealers)} locations")
                        return ScrapingResult(
                            status=ScrapingStatus.SUCCESS,
                            dealers=sitemap_dealers,
                            message=f"Successfully extracted {len(sitemap_dealers)} dealer locations via sitemap"
                        )
                return ScrapingResult(
                    status=ScrapingStatus.NO_DATA,
                    dealers=[],
                    message="No valid dealer locations found"
                )
            
            success_status = (ScrapingStatus.SUCCESS if len(processed_dealers) >= len(raw_dealers) * 0.8
                            else ScrapingStatus.PARTIAL_SUCCESS)
            
            if progress_callback:
                progress_callback(100, f"✅ Successfully extracted {len(processed_dealers)} dealers!")
            
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

    def _crawl_sitemap_locations(self, root_url: str, dealer_name: str) -> List[Dict[str, Any]]:
        """Attempt to discover and scrape individual location pages via sitemap(s).

        This is useful for sites that render a search-only locations page (no static list).
        """
        try:
            parsed = urlparse(root_url)
            base = f"{parsed.scheme}://{parsed.hostname}"
            index_url = base + "/sitemap-index.xml"
            self.logger.info(f"Fetching sitemap index: {index_url}")
            index_html = self.web_scraper.fetch_page(index_url, save_debug=False)
            if not index_html:
                return []

            # Find all URLs listed in <loc> tags
            loc_urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", index_html)
            # Collect candidate sitemaps and pages under /locations/
            location_sitemaps = [u for u in loc_urls if "/sitemap" in u and "/locations" in u and u.endswith('.xml')]
            location_pages = [u for u in loc_urls if "/locations/" in u and not u.endswith('.xml')]

            # Also fetch any location-specific sitemaps to expand pages
            for sm in location_sitemaps:
                self.logger.info(f"Fetching location sitemap: {sm}")
                sm_html = self.web_scraper.fetch_page(sm, save_debug=False)
                if not sm_html:
                    continue
                sm_locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm_html)
                for u in sm_locs:
                    if "/locations/" in u and not u.endswith('.xml'):
                        location_pages.append(u)

            # De-dup and cap to reasonable count
            unique_pages = list(dict.fromkeys(location_pages))[:500]
            if not unique_pages:
                return []

            all_dealers: List[Dict[str, Any]] = []
            for loc_url in unique_pages:
                html = self.web_scraper.fetch_page(loc_url, save_debug=False)
                if not html:
                    continue
                extracted = self.extractor.extract_dealer_data(html, loc_url)
                if extracted:
                    all_dealers.extend(extracted)

            # Final clean + dedupe
            processed = self.data_service.process_dealer_data(all_dealers, dealer_name=dealer_name)
            return processed
        except Exception as e:
            self.logger.warning(f"Sitemap crawl failed: {e}")
            return []