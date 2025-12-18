"""
Pytest configuration and shared fixtures for dealer scraper tests.
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock

# Sample HTML for testing
SAMPLE_DEALER_HTML = """
<!DOCTYPE html>
<html>
<head><title>Test Dealerships</title></head>
<body>
    <div class="dealer-location">
        <h3>ABC Toyota</h3>
        <p class="address">123 Main St, Boston, MA 02101</p>
        <p class="phone">(555) 123-4567</p>
    </div>
    <div class="dealer-location">
        <h3>XYZ Honda</h3>
        <p class="address">456 Oak Ave, Cambridge, MA 02139</p>
        <p class="phone">(555) 987-6543</p>
    </div>
</body>
</html>
"""

LITHIA_SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Lithia Locations</title></head>
<body>
    <div class="ddc-state-subheader">
        <h3>Alaska</h3>
    </div>
    <div class="ddc-subheader-locations">
        <div class="ddc-location-card">
            <h4>Lithia Chrysler Jeep Dodge of Anchorage</h4>
            <p>5601 A Street, Anchorage, AK 99518</p>
            <p>(907) 563-3330</p>
        </div>
    </div>
</body>
</html>
"""


@pytest.fixture
def sample_html():
    """Sample HTML with dealer locations."""
    return SAMPLE_DEALER_HTML


@pytest.fixture
def lithia_html():
    """Sample Lithia Motors HTML."""
    return LITHIA_SAMPLE_HTML


@pytest.fixture
def sample_dealer_data():
    """Sample dealer data dictionary."""
    return {
        'name': 'ABC Toyota',
        'street': '123 Main St',
        'city': 'Boston',
        'state': 'MA',
        'zip': '02101',
        'phone': '(555) 123-4567',
        'website': 'https://example.com',
        'page_url': 'https://example.com/locations'
    }


@pytest.fixture
def sample_dealers_list():
    """Sample list of dealer data."""
    return [
        {
            'name': 'ABC Toyota',
            'street': '123 Main St',
            'city': 'Boston',
            'state': 'MA',
            'zip': '02101',
            'phone': '(555) 123-4567',
            'website': 'https://example.com',
            'page_url': 'https://example.com/locations'
        },
        {
            'name': 'XYZ Honda',
            'street': '456 Oak Ave',
            'city': 'Cambridge',
            'state': 'MA',
            'zip': '02139',
            'phone': '(555) 987-6543',
            'website': 'https://example.com',
            'page_url': 'https://example.com/locations'
        }
    ]


@pytest.fixture
def duplicate_dealers_list():
    """Sample list with duplicate dealers."""
    return [
        {
            'name': 'ABC Toyota',
            'street': '123 Main St',
            'city': 'Boston',
            'state': 'MA',
            'zip': '02101',
            'phone': '(555) 123-4567',
            'website': 'https://example.com',
            'page_url': 'https://example.com/locations'
        },
        {
            'name': 'ABC Toyota',  # Duplicate
            'street': '123 Main St',
            'city': 'Boston',
            'state': 'MA',
            'zip': '02101',
            'phone': '(555) 123-4567',
            'website': 'https://example.com',
            'page_url': 'https://example.com/locations'
        },
        {
            'name': 'XYZ Honda',
            'street': '456 Oak Ave',
            'city': 'Cambridge',
            'state': 'MA',
            'zip': '02139',
            'phone': '(555) 987-6543',
            'website': 'https://example.com',
            'page_url': 'https://example.com/locations'
        }
    ]


@pytest.fixture
def mock_web_scraper():
    """Mock WebScraper instance."""
    scraper = Mock()
    scraper.fetch_page.return_value = SAMPLE_DEALER_HTML
    return scraper


@pytest.fixture
def mock_data_service():
    """Mock DataService instance."""
    service = Mock()
    service.process_dealer_data.return_value = [
        {
            'Dealership': 'ABC Toyota',
            'Dealer Group': 'Test Group',
            'Address': '123 Main St',
            'City': 'Boston',
            'State/Province': 'MA',
            'Postal Code': '02101',
            'Phone': '(555) 123-4567',
            'Website': 'https://example.com',
            'Country': 'USA'
        }
    ]
    return service


@pytest.fixture
def mock_playwright_response():
    """Mock Playwright subprocess response."""
    return {
        'success': True,
        'data': SAMPLE_DEALER_HTML,
        'error': None
    }


@pytest.fixture
def test_url():
    """Sample test URL."""
    return "https://example.com/locations"


@pytest.fixture
def test_dealer_name():
    """Sample dealer name."""
    return "Test Dealer Group"

