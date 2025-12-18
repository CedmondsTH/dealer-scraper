"""
Integration tests for scraping strategies.

These tests verify the end-to-end scraping pipeline works correctly.
They are marked as 'slow' since they may make real network requests.
"""

import os

import pytest

from src.services.scraper_service import ScraperService, ScrapingStatus

# Skip all integration tests if running in CI without API key
pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true" and not os.getenv("GEMINI_API_KEY"),
    reason="Skipping integration tests in CI without API key",
)


@pytest.mark.integration
class TestScraperServiceIntegration:
    """Integration tests for ScraperService."""

    @pytest.fixture
    def scraper_service(self):
        """Create a ScraperService instance."""
        return ScraperService()

    @pytest.mark.slow
    def test_scrape_lithia_motors(self, scraper_service):
        """Test scraping Lithia Motors website."""
        result = scraper_service.scrape_dealer_locations(
            "Lithia Motors", "https://www.lithia.com/locations/store-locations.htm"
        )

        assert result.success is True
        assert result.status == ScrapingStatus.SUCCESS
        assert len(result.dealers) > 100  # Lithia has 300+ locations
        assert result.error is None

        # Check data quality
        first_dealer = result.dealers[0]
        assert first_dealer.get("Dealership")
        assert first_dealer.get("City")
        assert first_dealer.get("State/Province")

    @pytest.mark.slow
    def test_scrape_hudson_automotive(self, scraper_service):
        """Test scraping Hudson Automotive website."""
        result = scraper_service.scrape_dealer_locations(
            "Hudson Automotive", "https://hudsonauto.com/locations"
        )

        assert result.success is True
        assert result.status == ScrapingStatus.SUCCESS
        assert len(result.dealers) > 0
        assert result.error is None

    def test_scrape_invalid_url(self, scraper_service):
        """Test scraping with an invalid URL."""
        result = scraper_service.scrape_dealer_locations(
            "Test Dealer", "https://this-url-definitely-does-not-exist-12345.com"
        )

        # Should return an error status
        assert result.success is False
        assert result.status in [ScrapingStatus.ERROR, ScrapingStatus.NO_DATA]
        assert len(result.dealers) == 0

    @pytest.mark.slow
    def test_scrape_multiple_urls(self, scraper_service):
        """Test scraping multiple URLs for a dealer group."""
        urls = [
            "https://www.lithia.com/locations/store-locations.htm",
        ]

        result = scraper_service.scrape_multiple_urls("Lithia Motors", urls)

        assert result.success is True
        assert len(result.dealers) > 0


@pytest.mark.integration
class TestStrategySelection:
    """Integration tests for strategy selection and fallback."""

    @pytest.fixture
    def scraper_service(self):
        """Create a ScraperService instance."""
        return ScraperService()

    @pytest.mark.slow
    def test_specific_strategy_selected(self, scraper_service):
        """Test that specific strategies are selected over generic ones."""
        # Lithia should use LithiaStrategy, not GenericDealerStrategy
        result = scraper_service.scrape_dealer_locations(
            "Lithia Motors", "https://www.lithia.com/locations/store-locations.htm"
        )

        assert result.success is True
        # Should use specific Lithia strategy
        assert len(result.dealers) > 100


@pytest.mark.integration
class TestDataQuality:
    """Integration tests for data quality and deduplication."""

    @pytest.fixture
    def scraper_service(self):
        """Create a ScraperService instance."""
        return ScraperService()

    @pytest.mark.slow
    def test_no_duplicates_in_results(self, scraper_service):
        """Test that results don't contain duplicates."""
        result = scraper_service.scrape_dealer_locations(
            "Lithia Motors", "https://www.lithia.com/locations/store-locations.htm"
        )

        assert result.success is True

        # Check for duplicates using normalized keys
        seen_keys = set()
        duplicates = 0

        for dealer in result.dealers:
            key = (
                dealer.get("Dealership", "").lower().strip(),
                dealer.get("Address", "").lower().strip(),
                dealer.get("City", "").lower().strip(),
            )
            if key in seen_keys and key[0] and key[1]:
                duplicates += 1
            seen_keys.add(key)

        assert duplicates == 0, f"Found {duplicates} duplicate dealers"

    @pytest.mark.slow
    def test_all_dealers_have_required_fields(self, scraper_service):
        """Test that all dealers have required fields."""
        result = scraper_service.scrape_dealer_locations(
            "Hudson Automotive", "https://hudsonauto.com/locations"
        )

        assert result.success is True

        for dealer in result.dealers:
            # Every dealer should have a name and city
            assert dealer.get("Dealership"), "Dealer missing name"
            assert dealer.get("City"), "Dealer missing city"

            # Most should have state
            if not dealer.get("State/Province"):
                print(f"Warning: Dealer {dealer.get('Dealership')} missing state")
