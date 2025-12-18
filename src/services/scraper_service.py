"""
Main scraper service providing high-level scraping operations.

This service coordinates web scraping, data extraction, and processing
operations with proper error handling and logging.
"""

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

from config import config
from src.exceptions import NoStrategyFoundError, PageFetchError, ScrapingError
from src.scrapers.strategies.new_llm_strategy import NewLLMExtractorStrategy
from src.scrapers.strategy_manager import get_configured_scraper
from src.services.data_service import DataService
from src.services.web_scraper import WebScraper

logger = logging.getLogger(__name__)


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

    def __init__(
        self,
        web_scraper: Optional[WebScraper] = None,
        data_service: Optional[DataService] = None,
    ):
        """
        Initialize the scraper service.

        Args:
            web_scraper: Optional WebScraper instance (creates new if None)
            data_service: Optional DataService instance (creates new if None)
        """
        self.web_scraper = web_scraper or WebScraper()
        self.data_service = data_service or DataService()
        self.extractor = get_configured_scraper()
        self.llm_fallback = NewLLMExtractorStrategy()

    def scrape_dealer_locations(
        self,
        dealer_name: str,
        url: str,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> ScrapingResult:
        """
        Scrape dealer locations from a given URL.

        Args:
            dealer_name: Name of the dealer group
            url: URL to scrape
            progress_callback: Optional callback function(percent: int, message: str)

        Returns:
            ScrapingResult with status and extracted data
        """
        try:
            logger.info(f"Starting scrape for {dealer_name} at {url}")

            # Step 1: Fetch web page content
            if progress_callback:
                progress_callback(25, "Fetching page content...")

            html_content = self.web_scraper.fetch_page(url)
            if not html_content:
                return ScrapingResult(
                    status=ScrapingStatus.FAILED,
                    dealers=[],
                    message="Failed to fetch page content",
                    error="Empty or invalid response from website",
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

            # Step 4: Retry Logic (Force Playwright)
            if not processed_dealers:
                processed_dealers = self._retry_with_playwright(
                    url, dealer_name, progress_callback
                )

            # Step 5: Fallback Logic (LLM & Sitemap)
            if not processed_dealers:
                processed_dealers = self._attempt_fallbacks(
                    url, dealer_name, html_content, progress_callback
                )

            # Final Status Determination
            if not processed_dealers:
                return ScrapingResult(
                    status=ScrapingStatus.NO_DATA,
                    dealers=[],
                    message="No valid dealer locations found",
                )

            success_status = (
                ScrapingStatus.SUCCESS
                if len(processed_dealers) >= len(raw_dealers) * 0.8
                else ScrapingStatus.PARTIAL_SUCCESS
            )

            if progress_callback:
                progress_callback(
                    100, f"✅ Successfully extracted {len(processed_dealers)} dealers!"
                )

            logger.info(
                f"Scraping completed: {len(processed_dealers)} dealers extracted"
            )

            return ScrapingResult(
                status=success_status,
                dealers=processed_dealers,
                message=f"Successfully extracted {len(processed_dealers)} dealer locations",
            )

        except PageFetchError as e:
            logger.error(f"Failed to fetch page for {dealer_name}: {e}")
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                dealers=[],
                message="Failed to fetch page",
                error=str(e),
            )
        except ScrapingError as e:
            logger.error(f"Scraping error for {dealer_name}: {e}")
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                dealers=[],
                message="Scraping operation failed",
                error=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error for {dealer_name}: {str(e)}", exc_info=True)
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                dealers=[],
                message="Unexpected error occurred",
                error=str(e),
            )

    def _retry_with_playwright(
        self, url: str, dealer_name: str, progress_callback
    ) -> List[Dict[str, Any]]:
        """Retry scraping using forced Playwright execution."""
        if progress_callback:
            progress_callback(70, "No dealers found, trying enhanced scraping...")

        logger.info(
            "No dealers after first pass; retrying with forced Playwright fetch..."
        )
        html_content_retry = self.web_scraper.fetch_page(url, force_playwright=True)

        if html_content_retry:
            raw_dealers_retry = self.extractor.extract_dealer_data(
                html_content_retry, url
            )
            return self.data_service.process_dealer_data(raw_dealers_retry, dealer_name)
        return []

    def _attempt_fallbacks(
        self, url: str, dealer_name: str, html_content: str, progress_callback
    ) -> List[Dict[str, Any]]:
        """Attempt LLM and Sitemap fallbacks."""
        # LLM Fallback
        try:
            if progress_callback:
                progress_callback(80, "🤖 Using AI to extract dealer information...")

            logger.info("Attempting LLM fallback extractor...")
            dealers_llm = self.llm_fallback._extract_with_llm(html_content, url)

            if dealers_llm:
                logger.info(f"LLM fallback extracted {len(dealers_llm)} dealers")
                processed = self.data_service.process_dealer_data(
                    dealers_llm, dealer_name
                )
                if processed:
                    return processed
        except Exception as e:
            logger.error(f"LLM fallback failed: {e}")

        # Sitemap Fallback
        logger.info("Attempting sitemap crawl...")
        return self._crawl_sitemap_locations(url, dealer_name)

    def scrape_multiple_urls(self, dealer_name: str, urls: List[str]) -> ScrapingResult:
        """
        Scrape multiple URLs for a dealer group concurrently.
        """
        all_dealers = []
        errors = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(self.scrape_dealer_locations, dealer_name, url): url
                for url in urls
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result.success:
                        all_dealers.extend(result.dealers)
                    elif result.error:
                        errors.append(f"{url}: {result.error}")
                except Exception as e:
                    errors.append(f"{url}: {str(e)}")

        unique_dealers = self.data_service.deduplicate_dealers(all_dealers)

        if not unique_dealers:
            return ScrapingResult(
                status=ScrapingStatus.NO_DATA,
                dealers=[],
                message="No valid dealers found across all URLs",
                error="; ".join(errors) if errors else None,
            )

        return ScrapingResult(
            status=ScrapingStatus.SUCCESS,
            dealers=unique_dealers,
            message=f"Successfully extracted {len(unique_dealers)} unique dealers from {len(urls)} URLs",
        )

    def _crawl_sitemap_locations(
        self, root_url: str, dealer_name: str
    ) -> List[Dict[str, Any]]:
        """Attempt to discover and scrape individual location pages via sitemap(s)."""
        try:
            parsed = urlparse(root_url)
            base = f"{parsed.scheme}://{parsed.hostname}"
            index_url = base + "/sitemap-index.xml"

            logger.info(f"Fetching sitemap index: {index_url}")
            index_html = self.web_scraper.fetch_page(index_url, save_debug=False)
            if not index_html:
                return []

            loc_urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", index_html)
            location_pages = [
                u for u in loc_urls if "/locations/" in u and not u.endswith(".xml")
            ]

            # Also check sub-sitemaps
            location_sitemaps = [
                u
                for u in loc_urls
                if "/sitemap" in u and "/locations" in u and u.endswith(".xml")
            ]
            for sm in location_sitemaps:
                sm_html = self.web_scraper.fetch_page(sm, save_debug=False)
                if sm_html:
                    sm_locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm_html)
                    location_pages.extend(
                        [
                            u
                            for u in sm_locs
                            if "/locations/" in u and not u.endswith(".xml")
                        ]
                    )

            unique_pages = list(dict.fromkeys(location_pages))[:500]
            if not unique_pages:
                logger.info("No location pages found in sitemap")
                return []

            logger.info(f"Found {len(unique_pages)} location pages in sitemap")
            # Use the concurrent scraper for these pages
            result = self.scrape_multiple_urls(dealer_name, unique_pages)
            return result.dealers

        except Exception as e:
            logger.warning(f"Sitemap crawl failed: {e}")
            return []
