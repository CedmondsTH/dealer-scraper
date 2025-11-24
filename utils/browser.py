"""
Browser automation utilities using Playwright.

This module handles all browser interactions, page loading,
and content extraction with proper error handling.
"""

from typing import Optional, List
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

from config.settings import config
from utils.logging import logger
from utils.parsers import extract_directory_links


class BrowserManager:
    """Manages browser automation for scraping."""
    
    def __init__(self):
        self.config = config
        self.logger = logger
    
    def scrape_page(self, url: str, dealer_name: str = "") -> str:
        """
        Scrape a single page and return HTML content.
        
        Args:
            url: URL to scrape
            dealer_name: Optional dealer name for logging
            
        Returns:
            HTML content of the page
        """
        self.logger.scrape_start(dealer_name or "Unknown", url)
        
        with sync_playwright() as p:
            browser = None
            try:
                # Launch browser
                browser = self._launch_browser(p)
                page = browser.new_page(viewport={"width": 1920, "height": 1080})
                
                # Navigate to page
                page.goto(url, wait_until="domcontentloaded", timeout=config.PLAYWRIGHT_TIMEOUT)
                
                # Wait for initial content
                self._wait_for_content(page, url)
                
                # Get initial HTML
                html = page.content()
                
                # Check if we need stealth mode for Dealer Inspire
                if self._is_dealer_inspire(html):
                    html = self._handle_dealer_inspire(p, url)
                elif self._needs_special_handling(url):
                    html = self._handle_special_cases(page, url)
                else:
                    # Standard page handling
                    html = self._handle_standard_page(page, html, url)
                
                return html
                
            except Exception as e:
                self.logger.error(f"Failed to scrape {url}: {e}")
                return ""
            finally:
                if browser:
                    browser.close()
    
    def scrape_multiple_pages(self, urls: List[str], dealer_name: str = "") -> List[str]:
        """
        Scrape multiple pages efficiently.
        
        Args:
            urls: List of URLs to scrape
            dealer_name: Optional dealer name for logging
            
        Returns:
            List of HTML content strings
        """
        html_results = []
        
        with sync_playwright() as p:
            browser = None
            try:
                browser = self._launch_browser(p)
                page = browser.new_page(viewport={"width": 1920, "height": 1080})
                
                for i, url in enumerate(urls):
                    try:
                        self.logger.info(f"Scraping subpage {i+1}/{len(urls)}: {url}")
                        
                        page.goto(url, wait_until="domcontentloaded", timeout=15000)
                        
                        # Wait for dealer cards to load
                        self._wait_for_dealer_cards(page)
                        
                        # Scroll to load all content
                        self._scroll_page(page, 2)
                        
                        html = page.content()
                        html_results.append(html)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to scrape subpage {url}: {e}")
                        html_results.append("")
                
            finally:
                if browser:
                    browser.close()
        
        return html_results
    
    def _launch_browser(self, playwright):
        """Launch browser with appropriate settings."""
        return playwright.chromium.launch(
            headless=config.BROWSER_HEADLESS,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ] if config.BROWSER_HEADLESS else []
        )
    
    def _wait_for_content(self, page, url: str):
        """Wait for specific content based on URL patterns."""
        try:
            # AutoBell specific
            if "autobell" in url.lower():
                page.wait_for_selector('.css-16af3dh li', timeout=20000)
                self.logger.debug("Waited for AutoBell locations")
            
            # Ken Garff specific
            elif "kengarff.com/contact-us" in url:
                page.wait_for_selector("div.well.matchable-heights", timeout=10000)
                self.logger.debug("Waited for Ken Garff elements")
            
            # Ken Ganley specific
            elif "kenganleyauto.com" in url.lower():
                # Wait for the panel bodies to load
                page.wait_for_selector("div.panel-body", timeout=15000)
                self.logger.debug("Waited for Ken Ganley panel elements")
            
            # General dealer content
            else:
                try:
                    page.wait_for_selector("div.panel-body.pad-1x.pad-bottom-x", timeout=10000)
                except PlaywrightTimeoutError:
                    pass
                    
        except PlaywrightTimeoutError:
            self.logger.debug(f"Timeout waiting for specific selectors on {url}")
    
    def _wait_for_inspire_content(self, page, url: str):
        """Enhanced waiting specifically for Dealer Inspire/Edwards sites."""
        try:
            # Edwards Auto Group specific selectors
            if "edwardsautogroup.com" in url:
                # Try multiple selectors that Edwards might use
                selectors_to_try = [
                    "div.col-lg-4",  # Bootstrap columns
                    "div.col-md-6", 
                    "div.card",      # Card containers
                    "div[class*='col-']",  # Any column class
                    "div.dealership-card",
                    "div.location-card"
                ]
                
                for selector in selectors_to_try:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        self.logger.debug(f"Edwards content loaded: {selector}")
                        break
                    except PlaywrightTimeoutError:
                        continue
            
            # General Inspire patterns
            else:
                try:
                    page.wait_for_selector("div.dealer-card, div.location, div.dealer-info", timeout=10000)
                    self.logger.debug("Inspire content loaded")
                except PlaywrightTimeoutError:
                    self.logger.debug("No specific Inspire selectors found")
                    
        except Exception as e:
            self.logger.debug(f"Error waiting for Inspire content: {e}")
    
    def _is_dealer_inspire(self, html: str) -> bool:
        """Check if page uses Dealer Inspire platform."""
        return (
            "dealerinspire.com" in html or
            "Dealer Inspire" in html or
            "dealerinspire" in html or
            # Edwards Auto Group specific detection
            "edwardsautogroup.com" in html or
            # Common Inspire patterns
            "inspire-" in html or
            "dealer-inspire" in html or
            # JavaScript patterns that indicate dynamic loading
            "loadDealerCards" in html or
            "dealerLocations" in html
        )
    
    def _handle_dealer_inspire(self, playwright, url: str) -> str:
        """Handle Dealer Inspire sites with stealth mode and enhanced waiting."""
        self.logger.debug("Dealer Inspire/Edwards detected, using enhanced stealth mode")
        
        browser = playwright.chromium.launch(
            headless=True,
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
        )
        
        page = context.new_page()
        
        # Navigate and wait for initial load
        page.goto(url, wait_until="domcontentloaded", timeout=config.PLAYWRIGHT_TIMEOUT)
        
        # Simple wait for content to load
        page.wait_for_timeout(2000)
        
        html = page.content()
        browser.close()
        
        return html
    
    def _needs_special_handling(self, url: str) -> bool:
        """Check if URL needs special handling."""
        return "kengarff.com/contact-us" in url
    
    def _handle_special_cases(self, page, url: str) -> str:
        """Handle special cases like Ken Garff contact page."""
        if "kengarff.com/contact-us" in url:
            # Scroll to load all dealer cards
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(500)
            
            html = page.content()
            
            # Log card count for debugging
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div.well.matchable-heights")
            self.logger.debug(f"After scrolling, found {len(cards)} Ken Garff dealer cards")
            
            return html
        
        return page.content()
    
    def _handle_standard_page(self, page, html: str, url: str) -> str:
        """Handle standard pages with possible directory detection."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Check if this page has dealer cards already
        has_dealer_cards = bool(
            soup.select("li.info-window, div.dealer-card, div.location-card, "
                       "div.g1-location-card, div.well.matchable-heights, "
                       "div.car-details, div.panel.panel-default") or
            # Check for All American Auto Group pattern
            [h3 for h3 in soup.select("h3.h4") if "all american" in h3.get_text(strip=True).lower()]
        )
        
        if has_dealer_cards:
            self.logger.debug("Dealer cards detected on initial load")
            return html
        
        # Check if this is a directory page
        subpage_links = self._extract_subpage_links(html, url)
        if subpage_links:
            self.logger.info(f"Detected directory page with {len(subpage_links)} subpages")
            # Scrape all subpages
            subpage_html = self.scrape_multiple_pages(subpage_links)
            # Return combined HTML or handle as needed
            return "\n".join(subpage_html)
        
        # Standard single page - scroll and return
        self._scroll_page(page, 10)
        return page.content()
    
    def _extract_subpage_links(self, html: str, url: str) -> List[str]:
        """Extract subpage links from directory page."""
        subpage_links = extract_directory_links(html, url)
        # Filter for specific patterns like Group 1
        return [link for link in subpage_links 
                if "/dealers.html?state=" in link or "/dealers?state=" in link]
    
    def _wait_for_dealer_cards(self, page):
        """Wait for dealer cards to load."""
        try:
            page.wait_for_selector(
                "div.dealer-card, div.location-card, div.g1-location-card", 
                timeout=10000
            )
        except PlaywrightTimeoutError:
            pass  # Continue without dealer cards
    
    def _scroll_page(self, page, iterations: int = 10):
        """Scroll page to load dynamic content."""
        for _ in range(iterations):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(config.SCROLL_DELAY)


# Global browser manager instance
browser_manager = BrowserManager()