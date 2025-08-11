"""
Web scraping service using Playwright.

This service handles all web scraping operations including
page fetching, browser management, and site-specific handling.
"""

import logging
import time
from typing import Optional, List
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

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
    headless: bool = True
    timeout: int = 60000
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    wait_for_network_idle: bool = False
    enable_stealth: bool = False


class WebScraper:
    """Service for web scraping operations using Playwright."""
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or ScrapingConfig()
        
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
        # Domains that frequently block plain requests
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        known_blocked_domains = {
            "ancira.com",
            "albrechtauto.com",
            "allensamuels.com",
            "baliseauto.com",
            "bakermotorcompany.com",
            "bakerautogroup.com",
        }

        # If explicitly forced or known to be hostile, go straight to Playwright subprocess
        if force_playwright or any(hostname.endswith(d) for d in known_blocked_domains):
            try:
                from .playwright_subprocess import fetch_with_playwright_subprocess
                self.logger.info(f"Using Playwright subprocess (forced) for: {url}")
                html_content = fetch_with_playwright_subprocess(url, self.config.timeout)
                if html_content:
                    if save_debug:
                        debug_file = Path(f"debug_playwright_{url.split('/')[-1]}.html")
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        self.logger.info(f"Debug HTML saved to {debug_file}")
                    return html_content
                self.logger.error(f"Playwright subprocess returned no content for {url}")
            except Exception as e:
                self.logger.error(f"Forced Playwright subprocess failed for {url}: {e}")
            # If forced and it failed, don't fall back to requests; just return None
            if force_playwright:
                return None
        # Try requests first (faster and more reliable)
        try:
            self.logger.info(f"Starting requests scrape for: {url}")
            import requests
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.config.timeout // 1000)
            response.raise_for_status()
            
            html_content = response.text
            self.logger.info(f"Successfully fetched {len(html_content)} characters via requests")
            
            if save_debug:
                debug_file = Path(f"debug_requests_{url.split('/')[-1]}.html")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.logger.info(f"Debug HTML saved to {debug_file}")
            
            return html_content
            
        except Exception as e:
            self.logger.warning(f"Requests failed for {url}: {e}. Trying with different headers...")
            
        # Try requests with different approach for blocked sites
        try:
            self.logger.info(f"Trying alternative request approach for: {url}")
            import requests
            import time
            
            # More sophisticated headers to bypass basic bot detection
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
            
            # Add a small delay to appear more human-like
            time.sleep(1)
            
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=self.config.timeout // 1000)
            response.raise_for_status()
            
            html_content = response.text
            self.logger.info(f"Successfully fetched {len(html_content)} characters via alternative requests")
            
            if save_debug:
                debug_file = Path(f"debug_alternative_{url.split('/')[-1]}.html")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.logger.info(f"Debug HTML saved to {debug_file}")
            
            return html_content
            
        except Exception as e2:
            self.logger.warning(f"Advanced requests failed for {url}: {e2}. Trying Playwright subprocess...")
            
        # Fallback to Playwright subprocess for heavily protected sites
        try:
            from .playwright_subprocess import fetch_with_playwright_subprocess
            
            self.logger.info(f"Using Playwright subprocess for: {url}")
            html_content = fetch_with_playwright_subprocess(url, self.config.timeout)
            
            if html_content:
                self.logger.info(f"Playwright subprocess success: {len(html_content)} characters")
                
                if save_debug:
                    debug_file = Path(f"debug_playwright_{url.split('/')[-1]}.html")
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    self.logger.info(f"Debug HTML saved to {debug_file}")
                
                return html_content
            else:
                self.logger.error(f"Playwright subprocess failed for {url}")
                return None
                
        except Exception as e3:
            self.logger.error(f"All scraping methods failed for {url}: {e3}")
            return None
    
