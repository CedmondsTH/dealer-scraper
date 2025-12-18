"""
Web scraping service using Playwright.

This service handles all web scraping operations including
page fetching, browser management, and site-specific handling.
"""

import logging
import time
from typing import Optional
from pathlib import Path
from urllib.parse import urlparse
import requests

from config import config
from src.exceptions import PageFetchError, PageTimeoutError, BrowserError

logger = logging.getLogger(__name__)

# Import will be handled gracefully if Playwright not available
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None
    PlaywrightTimeoutError = Exception


class WebScraper:
    """Service for web scraping operations using Playwright."""
    
    def __init__(self):
        """Initialize the web scraper with configuration."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright is not available. Please install it with: pip install playwright")
            raise BrowserError("Playwright is required for web scraping")
    
    def fetch_page(self, url: str, save_debug: bool = None, force_playwright: bool = False) -> Optional[str]:
        """
        Fetch HTML content from a URL.
        
        Args:
            url: URL to fetch
            save_debug: Whether to save debug HTML file (None = use config default)
            force_playwright: If True, skip requests and fetch with Playwright subprocess directly
            
        Returns:
            HTML content or None if failed
            
        Raises:
            PageFetchError: If all fetch attempts fail
        """
        if save_debug is None:
            save_debug = config.scraping.debug_files
        
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        
        # Check if domain is known to be blocked
        is_blocked = any(hostname.endswith(d) for d in config.blocked_domains)

        if force_playwright or is_blocked:
            return self._fetch_with_playwright(url, save_debug)

        # Try standard requests first
        content = self._fetch_with_requests(url, save_debug)
        if content:
            return content
            
        # Try alternative requests (headers)
        content = self._fetch_with_alternative_requests(url, save_debug)
        if content:
            return content
            
        # Fallback to Playwright
        return self._fetch_with_playwright(url, save_debug)

    def _fetch_with_requests(self, url: str, save_debug: bool) -> Optional[str]:
        """Attempt to fetch with standard requests."""
        try:
            logger.info(f"Starting requests scrape for: {url}")
            headers = {
                'User-Agent': config.scraping.user_agent
            }
            timeout_seconds = config.scraping.timeout // 1000
            response = requests.get(url, headers=headers, timeout=timeout_seconds)
            response.raise_for_status()
            
            self._save_debug(url, response.text, "requests", save_debug)
            logger.info(f"Successfully fetched {url} with requests")
            return response.text
        except requests.exceptions.Timeout:
            logger.warning(f"Requests timeout for {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Requests failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in requests fetch: {e}")
            return None

    def _fetch_with_alternative_requests(self, url: str, save_debug: bool) -> Optional[str]:
        """Attempt to fetch with alternative headers."""
        try:
            logger.info(f"Trying alternative request approach for: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            time.sleep(1)  # Brief delay to avoid rate limiting
            session = requests.Session()
            timeout_seconds = config.scraping.timeout // 1000
            response = session.get(url, headers=headers, timeout=timeout_seconds)
            response.raise_for_status()
            
            self._save_debug(url, response.text, "alternative", save_debug)
            logger.info(f"Successfully fetched {url} with alternative headers")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.warning(f"Alternative requests failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in alternative fetch: {e}")
            return None

    def _fetch_with_playwright(self, url: str, save_debug: bool) -> Optional[str]:
        """Fetch using Playwright subprocess."""
        try:
            from .playwright_subprocess import fetch_with_playwright_subprocess
            logger.info(f"Using Playwright subprocess for: {url}")
            
            html_content = fetch_with_playwright_subprocess(url, config.scraping.timeout)
            
            if html_content:
                self._save_debug(url, html_content, "playwright", save_debug)
                logger.info(f"Successfully fetched {url} with Playwright")
                return html_content
            else:
                logger.error(f"Playwright subprocess returned no content for {url}")
                raise PageFetchError(url, "Playwright returned empty content")
        except PageFetchError:
            raise
        except Exception as e:
            logger.error(f"Playwright fetch failed for {url}: {e}", exc_info=True)
            raise PageFetchError(url, str(e))

    def _save_debug(self, url: str, content: str, method: str, save: bool) -> None:
        """Save debug HTML file."""
        if not save:
            return
        try:
            filename = f"debug_{method}_{url.split('/')[-1]}.html"
            # Sanitize filename
            filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))
            debug_file = Path(filename)
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Debug HTML saved to {debug_file}")
        except Exception as e:
            logger.warning(f"Failed to save debug file: {e}")
