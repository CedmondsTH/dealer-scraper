"""Main entry point for the Dealership Scraper."""

import sys
import json
from config.settings import config
from scrapers import scraper_manager
from utils.browser import browser_manager
from utils.logging import logger


def scrape_dealerships_cli(dealer_name: str, url: str) -> list:
    """CLI interface for scraping dealerships."""
    try:
        config.validate()
        html = browser_manager.scrape_page(url, dealer_name)
        
        if not html:
            logger.error("Failed to retrieve HTML content")
            return []
        
        dealerships = scraper_manager.extract_dealerships(html, url, dealer_name)
        result = [dealership.to_dict() for dealership in dealerships]
        logger.scrape_complete(dealer_name, len(result))
        return result
        
    except Exception as e:
        logger.error(f"CLI scraping failed: {e}")
        raise


def main():
    """Main application entry point."""
    if len(sys.argv) > 1:
        # CLI mode
        if len(sys.argv) != 3:
            print("Usage: python main.py \"Dealer Name\" \"URL\"", file=sys.stderr)
            sys.exit(1)
        
        dealer_name, url = sys.argv[1], sys.argv[2]
        
        try:
            dealerships = scrape_dealerships_cli(dealer_name, url)
            # Ensure JSON output is flushed immediately and not buffered
            json_output = json.dumps(dealerships)
            print(json_output, flush=True)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Web interface mode
        try:
            from ui.streamlit_app import ui
            ui.run()
        except ImportError as e:
            print(f"Failed to import Streamlit UI: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    # Check if running with Streamlit
    if len(sys.argv) == 1:  # No command line args - running via Streamlit
        from ui.streamlit_app import ui
        ui.run()
    else:  # Command line args provided - CLI mode
        main()