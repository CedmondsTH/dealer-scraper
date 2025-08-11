"""
Legacy app.py replacement - maintains backward compatibility.

This file provides backward compatibility for the old app.py interface
while using the new professional architecture underneath.
"""

import sys
import json
from typing import List, Dict, Any

# Import the new professional system
from config import setup_logging
from core.scraper_service import ScraperService
from core.web_scraper import WebScraper, ScrapingConfig
from ui.streamlit_app import main as streamlit_main


def extract_dealer_data(html: str, page_url: str) -> List[Dict[str, Any]]:
    """
    Legacy function for backward compatibility.
    
    This function maintains the same interface as the old extract_dealer_data
    but uses the new modular scraper system underneath.
    """
    from scrapers.strategy_manager import get_configured_scraper
    
    # Get configured scraper with all strategies
    scraper = get_configured_scraper()
    
    # Extract dealer data using all available strategies
    dealers = scraper.extract_dealer_data(html, page_url)
    
    return dealers


def _scrape_rows(dealer_name: str, url: str) -> List[Dict[str, Any]]:
    """
    Legacy function for CLI scraping.
    
    This maintains the same interface as the old _scrape_rows function
    but uses the new professional web scraper.
    """
    print(f"Starting scrape for: {url}", file=sys.stderr)
    
    # Setup logging
    setup_logging()
    
    # Create web scraper with legacy settings
    config = ScrapingConfig(
        headless=True,
        timeout=60000,
        enable_stealth=True
    )
    web_scraper = WebScraper(config)
    
    # Create scraper service
    scraper_service = ScraperService(web_scraper=web_scraper)
    
    # Perform scraping
    result = scraper_service.scrape_dealer_locations(dealer_name, url)
    
    if result.success:
        print(f"Extraction complete: {len(result.dealers)} dealers found", file=sys.stderr)
        return result.dealers
    else:
        print(f"Scraping failed: {result.message}", file=sys.stderr)
        if result.error:
            print(f"Error details: {result.error}", file=sys.stderr)
        return []


# Legacy CLI support
if __name__ == "__main__" and len(sys.argv) > 1:
    if len(sys.argv) != 3:
        print("Usage: python app.py \"Dealer Name\" \"Locations URL\"", file=sys.stderr)
        sys.exit(1)
    
    name_arg, url_arg = sys.argv[1], sys.argv[2]
    try:
        rows = _scrape_rows(name_arg, url_arg)
        print(json.dumps(rows), flush=True)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    sys.exit(0)

# Legacy Streamlit support  
if __name__ == "__main__":
    # If no CLI args, run Streamlit interface
    streamlit_main()