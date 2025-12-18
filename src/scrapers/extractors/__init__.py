"""
Generic dealer extractors for various website patterns.

This package contains focused extractor classes for different dealer website formats,
extracted from the monolithic GenericDealerStrategy.
"""

from typing import Any, Dict, List, Protocol

from bs4 import BeautifulSoup


class DealerExtractor(Protocol):
    """Protocol for dealer data extractors."""

    def can_extract(self, soup: BeautifulSoup, page_url: str) -> bool:
        """Check if this extractor can handle the given page."""
        ...

    def extract(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealer data from the page."""
        ...

    @property
    def extractor_name(self) -> str:
        """Name of this extractor for logging."""
        ...
