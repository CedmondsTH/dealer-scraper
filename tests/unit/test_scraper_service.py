"""
Unit tests for scraper_service module.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.services.scraper_service import (ScraperService, ScrapingResult,
                                          ScrapingStatus)


class TestScraperService:
    """Test suite for ScraperService class."""

    def test_scraper_service_initialization(self):
        """Test ScraperService initializes correctly."""
        service = ScraperService()

        assert service.web_scraper is not None
        assert service.data_service is not None
        assert service.extractor is not None

    def test_scraper_service_with_mocks(self, mock_web_scraper, mock_data_service):
        """Test ScraperService with mock dependencies."""
        service = ScraperService(
            web_scraper=mock_web_scraper, data_service=mock_data_service
        )

        assert service.web_scraper == mock_web_scraper
        assert service.data_service == mock_data_service

    @patch("src.services.scraper_service.get_configured_scraper")
    def test_scrape_dealer_locations_success(
        self,
        mock_get_scraper,
        mock_web_scraper,
        mock_data_service,
        test_dealer_name,
        test_url,
    ):
        """Test successful dealer location scraping."""
        # Setup mocks
        mock_extractor = Mock()
        mock_extractor.extract_dealer_data.return_value = [
            {
                "name": "ABC Toyota",
                "street": "123 Main St",
                "city": "Boston",
                "state": "MA",
                "zip": "02101",
                "phone": "(555) 123-4567",
                "website": "https://example.com",
                "page_url": test_url,
            }
        ]
        mock_get_scraper.return_value = mock_extractor

        # Create service and scrape
        service = ScraperService(
            web_scraper=mock_web_scraper, data_service=mock_data_service
        )
        result = service.scrape_dealer_locations(test_dealer_name, test_url)

        # Assertions
        assert result.status == ScrapingStatus.SUCCESS
        assert result.success is True
        assert len(result.dealers) > 0
        assert result.error is None

    @patch("src.services.scraper_service.get_configured_scraper")
    def test_scrape_dealer_locations_no_data(
        self, mock_get_scraper, test_dealer_name, test_url
    ):
        """Test scraping when no data is found."""
        # Setup mocks to return empty results
        mock_web_scraper = Mock()
        mock_web_scraper.fetch_page.return_value = (
            "<html><body>No dealers here</body></html>"
        )

        mock_data_service = Mock()
        mock_data_service.process_dealer_data.return_value = []

        mock_extractor = Mock()
        mock_extractor.extract_dealer_data.return_value = []
        mock_get_scraper.return_value = mock_extractor

        service = ScraperService(
            web_scraper=mock_web_scraper, data_service=mock_data_service
        )

        # Mock the retry and fallback methods to return empty lists
        service._retry_with_playwright = Mock(return_value=[])
        service._attempt_fallbacks = Mock(return_value=[])

        result = service.scrape_dealer_locations(test_dealer_name, test_url)

        # Assertions
        assert result.status == ScrapingStatus.NO_DATA
        assert len(result.dealers) == 0
        assert not result.success

    @patch("src.services.scraper_service.get_configured_scraper")
    def test_scrape_dealer_locations_with_progress_callback(
        self,
        mock_get_scraper,
        mock_web_scraper,
        mock_data_service,
        test_dealer_name,
        test_url,
    ):
        """Test scraping with progress callback."""
        progress_calls = []

        def progress_callback(percent, message):
            progress_calls.append((percent, message))

        mock_extractor = Mock()
        mock_extractor.extract_dealer_data.return_value = []
        mock_get_scraper.return_value = mock_extractor

        service = ScraperService(
            web_scraper=mock_web_scraper, data_service=mock_data_service
        )
        service._retry_with_playwright = Mock(return_value=[])
        service._attempt_fallbacks = Mock(return_value=[])

        result = service.scrape_dealer_locations(
            test_dealer_name, test_url, progress_callback=progress_callback
        )

        # Verify progress callbacks were made
        assert len(progress_calls) > 0
        # Check that percent values are reasonable
        for percent, message in progress_calls:
            assert 0 <= percent <= 100
            assert isinstance(message, str)

    def test_scrape_dealer_locations_failed_fetch(self, test_dealer_name, test_url):
        """Test handling of failed page fetch."""
        mock_web_scraper = Mock()
        mock_web_scraper.fetch_page.return_value = None  # Simulate failed fetch

        service = ScraperService(web_scraper=mock_web_scraper)
        result = service.scrape_dealer_locations(test_dealer_name, test_url)

        assert result.status == ScrapingStatus.FAILED
        assert not result.success
        assert result.error is not None


@pytest.mark.unit
class TestScrapingResult:
    """Test ScrapingResult dataclass."""

    def test_scraping_result_success_property(self):
        """Test success property for different statuses."""
        # SUCCESS status
        result = ScrapingResult(
            status=ScrapingStatus.SUCCESS, dealers=[], message="Success"
        )
        assert result.success is True

        # PARTIAL_SUCCESS status
        result = ScrapingResult(
            status=ScrapingStatus.PARTIAL_SUCCESS, dealers=[], message="Partial"
        )
        assert result.success is True

        # FAILED status
        result = ScrapingResult(
            status=ScrapingStatus.FAILED, dealers=[], message="Failed"
        )
        assert result.success is False

        # NO_DATA status
        result = ScrapingResult(
            status=ScrapingStatus.NO_DATA, dealers=[], message="No data"
        )
        assert result.success is False

    def test_scraping_result_with_error(self):
        """Test ScrapingResult with error message."""
        result = ScrapingResult(
            status=ScrapingStatus.FAILED,
            dealers=[],
            message="Failed",
            error="Connection timeout",
        )

        assert result.error == "Connection timeout"
        assert not result.success

    def test_scraping_result_with_dealers(self, sample_dealers_list):
        """Test ScrapingResult with dealer data."""
        result = ScrapingResult(
            status=ScrapingStatus.SUCCESS,
            dealers=sample_dealers_list,
            message="Success",
        )

        assert len(result.dealers) == 2
        assert result.success is True
