"""
Custom exceptions for the Dealer Scraper application.

This module defines domain-specific exceptions for better error handling
and more informative error messages.
"""


class DealerScraperError(Exception):
    """Base exception for all dealer scraper errors."""
    pass


class ConfigurationError(DealerScraperError):
    """Raised when there's a configuration problem."""
    pass


class ScrapingError(DealerScraperError):
    """Base exception for scraping-related errors."""
    pass


class PageFetchError(ScrapingError):
    """Raised when unable to fetch a web page."""
    
    def __init__(self, url: str, reason: str = "Unknown error"):
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch page '{url}': {reason}")


class PageTimeoutError(ScrapingError):
    """Raised when a page fetch times out."""
    
    def __init__(self, url: str, timeout: int):
        self.url = url
        self.timeout = timeout
        super().__init__(f"Page fetch timed out after {timeout}ms: {url}")


class NoStrategyFoundError(ScrapingError):
    """Raised when no scraping strategy can handle a page."""
    
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"No scraping strategy found for: {url}")


class ExtractionError(ScrapingError):
    """Raised when data extraction fails."""
    
    def __init__(self, strategy_name: str, reason: str = "Unknown error"):
        self.strategy_name = strategy_name
        self.reason = reason
        super().__init__(f"Extraction failed in {strategy_name}: {reason}")


class DataValidationError(DealerScraperError):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, value: str, reason: str = "Invalid value"):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Validation failed for {field}='{value}': {reason}")


class DataProcessingError(DealerScraperError):
    """Raised when data processing fails."""
    pass


class ExportError(DealerScraperError):
    """Raised when data export fails."""
    
    def __init__(self, format_type: str, reason: str = "Unknown error"):
        self.format_type = format_type
        self.reason = reason
        super().__init__(f"Failed to export to {format_type}: {reason}")


class BrowserError(ScrapingError):
    """Raised when browser automation fails."""
    
    def __init__(self, reason: str = "Browser error"):
        self.reason = reason
        super().__init__(f"Browser automation failed: {reason}")


class APIError(DealerScraperError):
    """Raised when an external API call fails."""
    
    def __init__(self, api_name: str, reason: str = "Unknown error"):
        self.api_name = api_name
        self.reason = reason
        super().__init__(f"{api_name} API error: {reason}")


class RateLimitError(APIError):
    """Raised when an API rate limit is exceeded."""
    
    def __init__(self, api_name: str, retry_after: int = None):
        self.retry_after = retry_after
        message = f"{api_name} rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(api_name, message)

