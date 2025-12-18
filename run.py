"""
Main entry point for the Dealer Scraper application.

This module provides both CLI and web interface modes.
Run without arguments to start the Streamlit web interface.
Run with arguments to use CLI mode for scripting.
"""

import sys
import json
import logging
from typing import List, Dict, Any

# Import centralized configuration
from config import config, setup_logging

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)


def run_cli_mode(dealer_name: str, url: str) -> List[Dict[str, Any]]:
    """
    Run scraper in CLI mode.
    
    Args:
        dealer_name: Name of the dealer group
        url: URL to scrape
        
    Returns:
        List of dealer dictionaries
        
    Raises:
        Various exceptions from scraping operations
    """
    from src.services.scraper_service import ScraperService
    from src.exceptions import DealerScraperError
    
    try:
        logger.info(f"Starting CLI scrape for {dealer_name} at {url}")
        
        # Validate configuration
        config.validate()
        
        # Initialize service
        scraper_service = ScraperService()
        
        # Perform scraping
        result = scraper_service.scrape_dealer_locations(dealer_name, url)
        
        if not result.success:
            logger.error(f"Scraping failed: {result.message}")
            if result.error:
                logger.error(f"Error details: {result.error}")
            return []
        
        logger.info(f"Successfully extracted {len(result.dealers)} dealers")
        return result.dealers
        
    except DealerScraperError as e:
        logger.error(f"Scraping error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise


def run_web_mode() -> None:
    """Run scraper in web interface mode."""
    try:
        logger.info("Starting Streamlit web interface")
        from src.ui.streamlit_app import run_app
        run_app()
    except ImportError as e:
        logger.error(f"Failed to import Streamlit UI: {e}")
        print("Error: Streamlit is not installed. Install it with: pip install streamlit", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start web interface: {e}", exc_info=True)
        sys.exit(1)


def print_usage() -> None:
    """Print CLI usage information."""
    print("""
Dealer Scraper - Professional automotive dealership data extraction

Usage:
    python run.py                                    Start web interface
    python run.py <dealer_name> <url>                CLI mode: scrape single URL
    python run.py --help                             Show this help message

Examples:
    python run.py                                    # Start Streamlit UI
    python run.py "Lithia Motors" "https://lithia.com/locations"

Environment:
    Configure via .env file or environment variables.
    See env.example for available options.
    
    Required:
        GEMINI_API_KEY - API key for Gemini AI fallback
    """)


def main() -> None:
    """Main application entry point."""
    try:
        # Check for help flag
        if len(sys.argv) > 1 and sys.argv[1] in ('--help', '-h', 'help'):
            print_usage()
            sys.exit(0)
        
        # CLI mode: requires dealer name and URL
        if len(sys.argv) == 3:
            dealer_name = sys.argv[1]
            url = sys.argv[2]
            
            dealers = run_cli_mode(dealer_name, url)
            
            # Output JSON to stdout for piping/scripting
            print(json.dumps(dealers, indent=2))
            sys.exit(0)
        
        # CLI mode with wrong number of arguments
        elif len(sys.argv) > 1:
            print("Error: Invalid arguments", file=sys.stderr)
            print_usage()
            sys.exit(1)
        
        # Web mode (no arguments)
        else:
            run_web_mode()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

