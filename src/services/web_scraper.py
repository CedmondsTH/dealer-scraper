"""
Web scraping service using Playwright.

This service handles all web scraping operations including
page fetching, browser management, and site-specific handling.
"""

import logging
import time
from typing import Optional
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import requests

from ..config import config

# Import will be handled gracefully if Playwright not available
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None
    PlaywrightTimeoutError = Exception


@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations."""
    headless: bool = config.HEADLESS
    timeout: int = config.DEFAULT_TIMEOUT
    viewport_width: int = config.VIEWPORT_WIDTH
    viewport_height: int = config.VIEWPORT_HEIGHT
    user_agent: str = config.USER_AGENT


class WebScraper:
    """Service for web scraping operations using Playwright."""
    
    def __init__(self, scraping_config: Optional[ScrapingConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.config = scraping_config or ScrapingConfig()
        
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright is not available. Please install it with: pip install playwright")
            raise ImportError("Playwright is required for web scraping")
    
    def fetch_page(self, url: str, save_debug: bool = True, force_playwright: bool = False) -> Optional[str]:
        """
        Fetch HTML content from a URL.
        
        Args:
            url: URL to fetch
            save_debug: Whether to save debug HTML file
            force_playwright: If True, skip requests and fetch with Playwright subprocess directly
            
        Returns:
            HTML content or None if failed
        """
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        
        # Check if domain is known to be blocked
        is_blocked = any(hostname.endswith(d) for d in config.KNOWN_BLOCKED_DOMAINS)

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
            self.logger.info(f"Starting requests scrape for: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=self.config.timeout // 1000)
            response.raise_for_status()
            
            self._save_debug(url, response.text, "requests", save_debug)
            return response.text
        except Exception as e:
            self.logger.warning(f"Requests failed for {url}: {e}")
            return None

    def _fetch_with_alternative_requests(self, url: str, save_debug: bool) -> Optional[str]:
        """Attempt to fetch with alternative headers."""
        try:
            self.logger.info(f"Trying alternative request approach for: {url}")
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
            time.sleep(1)
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=self.config.timeout // 1000)
            response.raise_for_status()
            
            self._save_debug(url, response.text, "alternative", save_debug)
            return response.text
        except Exception as e:
            self.logger.warning(f"Advanced requests failed for {url}: {e}")
            return None

    def _fetch_with_playwright(self, url: str, save_debug: bool) -> Optional[str]:
        """Fetch using Playwright subprocess."""
        try:
            from .playwright_subprocess import fetch_with_playwright_subprocess
            self.logger.info(f"Using Playwright subprocess for: {url}")
            
            html_content = fetch_with_playwright_subprocess(url, self.config.timeout)
            
            if html_content:
                self._save_debug(url, html_content, "playwright", save_debug)
                return html_content
            else:
                self.logger.error(f"Playwright subprocess returned no content for {url}")
                return None
        except Exception as e:
            self.logger.error(f"Playwright fetch failed for {url}: {e}")
            return None

    def _save_debug(self, url: str, content: str, method: str, save: bool):
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
            self.logger.info(f"Debug HTML saved to {debug_file}")
        except Exception as e:
            self.logger.warning(f"Failed to save debug file: {e}")
