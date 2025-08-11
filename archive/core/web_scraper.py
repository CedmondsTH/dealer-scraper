"""
Web scraping service using Playwright.

This service handles all web scraping operations including
page fetching, browser management, and site-specific handling.
"""

import logging
import time
from typing import Optional, List
from dataclasses import dataclass

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
    
    def fetch_page(self, url: str, save_debug: bool = True) -> Optional[str]:
        """
        Fetch HTML content from a URL.
        
        Args:
            url: URL to fetch
            save_debug: Whether to save debug HTML file
            
        Returns:
            HTML content or None if failed
        """
        try:
            self.logger.info(f"Starting Playwright scrape for: {url}")
            
            with sync_playwright() as p:
                # Initial browser launch
                browser = p.chromium.launch(headless=self.config.headless)
                page = browser.new_page(viewport={
                    "width": self.config.viewport_width, 
                    "height": self.config.viewport_height
                })
                
                # Navigate to page
                page.goto(url, wait_until="domcontentloaded", timeout=self.config.timeout)
                
                # Wait for specific selectors that might be present
                self._wait_for_common_selectors(page)
                
                # Get initial HTML
                html = page.content()
                
                # Check if we need stealth mode (e.g., for Dealer Inspire sites)
                if self._needs_stealth_mode(html):
                    self.logger.info("Dealer Inspire detected, using stealth mode")
                    browser.close()
                    html = self._fetch_with_stealth(p, url)
                else:
                    # Handle special cases
                    html = self._handle_special_cases(page, url, html)
                    browser.close()
                
                # Save debug file if requested
                if save_debug and html:
                    self._save_debug_html(html, url)
                
                self.logger.info("Finished Playwright scrape")
                return html
                
        except Exception as e:
            self.logger.error(f"Failed to fetch page {url}: {str(e)}", exc_info=True)
            return None
    
    def _wait_for_common_selectors(self, page) -> None:
        """Wait for common selectors that might indicate content is loaded."""
        selectors_to_try = [
            '.css-16af3dh li',  # AutoBell locations
            'div.dealer-card',   # Generic dealer cards
            'li.info-window',    # Lithia
            'div.well.matchable-heights',  # AutoCanada/Ken Garff
        ]
        
        for selector in selectors_to_try:
            try:
                page.wait_for_selector(selector, timeout=5000)
                self.logger.debug(f"Found selector: {selector}")
                break
            except:
                continue
    
    def _needs_stealth_mode(self, html: str) -> bool:
        """Check if the page requires stealth mode."""
        stealth_indicators = [
            "dealerinspire.com",
            "Dealer Inspire",
            "dealerinspire"
        ]
        
        return any(indicator in html for indicator in stealth_indicators)
    
    def _fetch_with_stealth(self, playwright, url: str) -> str:
        """Fetch page using stealth settings."""
        browser = playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox', 
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        context = browser.new_context(
            user_agent=self.config.user_agent,
            viewport={'width': self.config.viewport_width, 'height': self.config.viewport_height},
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
        )
        
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=self.config.timeout)
        html = page.content()
        browser.close()
        
        return html
    
    def _handle_special_cases(self, page, url: str, html: str) -> str:
        """Handle special cases for specific websites."""
        
        # Ken Garff contact-us page
        if "kengarff.com/contact-us" in url:
            return self._handle_ken_garff(page)
        
        # Check for directory pages that might need subpage scraping
        if self._is_directory_page(html, url):
            return self._handle_directory_page(page, url, html)
        
        # Default case - scroll to load content
        return self._scroll_and_load(page)
    
    def _handle_ken_garff(self, page) -> str:
        """Special handling for Ken Garff pages."""
        try:
            page.wait_for_selector("div.well.matchable-heights", timeout=10000)
        except:
            self.logger.debug("No Ken Garff cards found after initial load")
        
        # Scroll to load all cards
        for _ in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(500)
        
        return page.content()
    
    def _is_directory_page(self, html: str, url: str) -> bool:
        """Check if this appears to be a directory page."""
        # This would contain logic to detect directory patterns
        # For now, simplified
        return False
    
    def _handle_directory_page(self, page, url: str, html: str) -> str:
        """Handle directory pages with subpages."""
        # This would contain logic to scrape subpages
        # For now, return the main page
        return html
    
    def _scroll_and_load(self, page) -> str:
        """Default scrolling behavior to load dynamic content."""
        try:
            page.wait_for_selector("div.panel-body.pad-1x.pad-bottom-x", timeout=30000)
        except:
            pass
        
        # Scroll multiple times to load content
        for _ in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
        
        return page.content()
    
    def _save_debug_html(self, html: str, url: str) -> None:
        """Save HTML content for debugging."""
        try:
            filename = "debug_scrape.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            self.logger.debug(f"Saved debug HTML to {filename}")
        except Exception as e:
            self.logger.warning(f"Failed to save debug HTML: {str(e)}")