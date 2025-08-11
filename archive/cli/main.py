"""
Main CLI interface for the dealer scraping application.

This module provides the command-line interface with proper
argument parsing, help text, and error handling.
"""

import argparse
import json
import sys
from typing import List, Optional

from config import setup_logging, get_settings
from core.scraper_service import ScraperService, ScrapingStatus


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    
    parser = argparse.ArgumentParser(
        description="Scrape dealer locations from automotive dealer websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scrape "Lithia Motors" "https://www.lithia.com/locations"
  %(prog)s scrape "AutoNation" "https://www.autonation.com/locations" --format json
  %(prog)s scrape "Dealer Group" "https://example.com" --debug --headless false
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser(
        'scrape', 
        help='Scrape dealer locations from a website'
    )
    scrape_parser.add_argument(
        'dealer_name',
        help='Name of the dealer group'
    )
    scrape_parser.add_argument(
        'url',
        help='URL of the dealer locations page'
    )
    scrape_parser.add_argument(
        '--format',
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    scrape_parser.add_argument(
        '--output',
        '-o',
        help='Output file path (default: stdout)'
    )
    scrape_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose logging'
    )
    scrape_parser.add_argument(
        '--headless',
        type=str,
        choices=['true', 'false'],
        help='Run browser in headless mode (default: true)'
    )
    scrape_parser.add_argument(
        '--timeout',
        type=int,
        help='Scraping timeout in milliseconds (default: 60000)'
    )
    
    # List strategies command
    list_parser = subparsers.add_parser(
        'list-strategies',
        help='List all available scraping strategies'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate a URL without scraping'
    )
    validate_parser.add_argument(
        'url',
        help='URL to validate'
    )
    
    return parser


def handle_scrape_command(args) -> int:
    """Handle the scrape command."""
    
    try:
        # Setup environment overrides from CLI args
        if args.debug:
            import os
            os.environ['DEBUG'] = 'true'
            os.environ['LOG_LEVEL'] = 'DEBUG'
        
        if args.headless:
            import os
            os.environ['SCRAPING_HEADLESS'] = args.headless
        
        if args.timeout:
            import os
            os.environ['SCRAPING_TIMEOUT'] = str(args.timeout)
        
        # Initialize logging
        setup_logging()
        
        # Create scraper service
        scraper_service = ScraperService()
        
        # Perform scraping
        result = scraper_service.scrape_dealer_locations(args.dealer_name, args.url)
        
        # Handle result
        if result.status == ScrapingStatus.FAILED:
            print(f"Error: {result.message}", file=sys.stderr)
            if result.error:
                print(f"Details: {result.error}", file=sys.stderr)
            return 1
        
        if result.status == ScrapingStatus.NO_DATA:
            print(f"Warning: {result.message}", file=sys.stderr)
            return 0
        
        # Format output
        if args.format == 'json':
            output_data = json.dumps(result.dealers, indent=2)
        elif args.format == 'csv':
            from core.data_service import DataService
            data_service = DataService()
            output_data = data_service.export_to_csv(result.dealers)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_data)
            print(f"Results written to {args.output}", file=sys.stderr)
        else:
            print(output_data)
        
        # Print summary to stderr
        print(f"Successfully extracted {len(result.dealers)} dealers", file=sys.stderr)
        
        return 0
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def handle_list_strategies_command(args) -> int:
    """Handle the list-strategies command."""
    
    try:
        from scrapers.scraper_registry import scraper_registry
        from scrapers.strategy_manager import initialize_strategies
        
        # Initialize strategies
        initialize_strategies()
        
        # List strategies
        strategies = scraper_registry.list_strategies()
        
        print("Available scraping strategies:")
        for i, strategy in enumerate(strategies, 1):
            print(f"  {i}. {strategy}")
        
        return 0
        
    except Exception as e:
        print(f"Error listing strategies: {str(e)}", file=sys.stderr)
        return 1


def handle_validate_command(args) -> int:
    """Handle the validate command."""
    
    try:
        # Basic URL validation
        from urllib.parse import urlparse
        
        parsed = urlparse(args.url)
        if not all([parsed.scheme, parsed.netloc]):
            print(f"Invalid URL: {args.url}", file=sys.stderr)
            return 1
        
        print(f"URL appears valid: {args.url}")
        print(f"  Scheme: {parsed.scheme}")
        print(f"  Domain: {parsed.netloc}")
        print(f"  Path: {parsed.path}")
        
        return 0
        
    except Exception as e:
        print(f"Error validating URL: {str(e)}", file=sys.stderr)
        return 1


def cli_main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        argv: Command line arguments. If None, uses sys.argv
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate handler
    if args.command == 'scrape':
        return handle_scrape_command(args)
    elif args.command == 'list-strategies':
        return handle_list_strategies_command(args)
    elif args.command == 'validate':
        return handle_validate_command(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1


def main() -> None:
    """Main entry point for the CLI application."""
    sys.exit(cli_main())


if __name__ == '__main__':
    main()