"""
Main entry point for the dealer scraping application.

This module provides the main entry point that can run either
the CLI interface or the Streamlit web interface.
"""

import sys
import os
from typing import List, Optional

def main(argv: Optional[List[str]] = None) -> int:
    """
    Main application entry point.
    
    This function determines whether to run the CLI or web interface
    based on command line arguments.
    
    Args:
        argv: Command line arguments. If None, uses sys.argv
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    
    if argv is None:
        argv = sys.argv[1:]
    
    # If no arguments or first argument is 'web', run Streamlit
    if not argv or argv[0] == 'web':
        return run_web_interface()
    
    # If we have arguments, run CLI
    return run_cli_interface(argv)


def run_cli_interface(argv: List[str]) -> int:
    """Run the command-line interface."""
    try:
        from cli.main import cli_main
        return cli_main(argv)
    except ImportError as e:
        print(f"Error: Failed to import CLI module: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: CLI failed: {e}", file=sys.stderr)
        return 1


def run_web_interface() -> int:
    """Run the Streamlit web interface."""
    try:
        # Set up environment for Streamlit
        os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
        os.environ.setdefault('STREAMLIT_SERVER_PORT', '8501')
        
        from ui.streamlit_app import main as streamlit_main
        streamlit_main()
        return 0
        
    except ImportError as e:
        print(f"Error: Failed to import Streamlit module: {e}", file=sys.stderr)
        print("Make sure Streamlit is installed: pip install streamlit", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: Web interface failed: {e}", file=sys.stderr)
        return 1


def legacy_cli_support() -> int:
    """
    Support for legacy CLI usage: python app.py "dealer" "url"
    
    This maintains backward compatibility with the old interface.
    """
    if len(sys.argv) == 3:
        # Legacy format: python app.py "dealer_name" "url"
        dealer_name = sys.argv[1]
        url = sys.argv[2]
        
        # Convert to new CLI format
        new_argv = ['scrape', dealer_name, url, '--format', 'json']
        return run_cli_interface(new_argv)
    
    return 1


if __name__ == "__main__":
    # Check for legacy CLI usage first
    if len(sys.argv) == 3:
        exit_code = legacy_cli_support()
    else:
        exit_code = main()
    
    sys.exit(exit_code)