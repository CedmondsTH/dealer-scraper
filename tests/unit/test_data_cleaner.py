"""
Unit tests for data_cleaner module.
"""

import pytest

from src.utils.data_cleaner import DataCleaner


@pytest.fixture
def data_cleaner():
    """DataCleaner instance for testing."""
    return DataCleaner()


class TestDataCleaner:
    """Test suite for DataCleaner class."""

    def test_is_valid_dealership_with_valid_data(
        self, data_cleaner, sample_dealer_data
    ):
        """Test validation of valid dealership data."""
        assert data_cleaner.is_valid_dealership(sample_dealer_data) is True

    def test_is_valid_dealership_with_invalid_name(self, data_cleaner):
        """Test validation rejects invalid dealership names."""
        invalid_dealer = {
            "name": "Locations",  # Invalid name from Constants.INVALID_DEALERSHIP_NAMES
            "street": "123 Main St",
            "city": "Boston",
            "state": "MA",
        }
        assert data_cleaner.is_valid_dealership(invalid_dealer) is False

    def test_is_valid_dealership_with_missing_name(self, data_cleaner):
        """Test validation rejects dealers with missing name."""
        invalid_dealer = {
            "name": "",
            "street": "123 Main St",
            "city": "Boston",
            "state": "MA",
        }
        assert data_cleaner.is_valid_dealership(invalid_dealer) is False

    def test_is_valid_dealership_with_missing_city(self, data_cleaner):
        """Test validation rejects dealers with missing city."""
        invalid_dealer = {
            "name": "ABC Toyota",
            "street": "123 Main St",
            "city": "",
            "state": "MA",
        }
        assert data_cleaner.is_valid_dealership(invalid_dealer) is False

    def test_normalize_name_title_case(self, data_cleaner):
        """Test name normalization to title case."""
        assert data_cleaner.normalize_name("abc toyota") == "Abc Toyota"
        assert data_cleaner.normalize_name("ABC TOYOTA") == "Abc Toyota"

    def test_normalize_name_preserves_special_cases(self, data_cleaner):
        """Test name normalization preserves special cases like LLC, BMW."""
        assert "LLC" in data_cleaner.normalize_name("abc motors llc")
        assert "BMW" in data_cleaner.normalize_name("abc bmw")

    def test_normalize_city(self, data_cleaner):
        """Test city name normalization."""
        assert data_cleaner.normalize_city("boston") == "Boston"
        assert data_cleaner.normalize_city("BOSTON") == "Boston"
        assert data_cleaner.normalize_city("  boston  ") == "Boston"

    def test_normalize_website(self, data_cleaner):
        """Test website URL normalization."""
        assert data_cleaner.normalize_website("example.com") == "https://example.com"
        assert (
            data_cleaner.normalize_website("http://example.com") == "http://example.com"
        )
        assert (
            data_cleaner.normalize_website("https://example.com")
            == "https://example.com"
        )

    def test_extract_phone_number(self, data_cleaner):
        """Test phone number extraction."""
        assert "555-123-4567" in data_cleaner.extract_phone_number(
            "Call us at (555) 123-4567"
        )
        assert "5551234567" in data_cleaner.extract_phone_number("Phone: 5551234567")

    def test_classify_dealer_type(self, data_cleaner):
        """Test dealer type classification."""
        assert "New Car Dealer" in data_cleaner.classify_dealer_type("ABC Toyota")
        assert "Used Car Dealer" in data_cleaner.classify_dealer_type(
            "Bob's Pre-Owned Cars"
        )
        assert "Service Center" in data_cleaner.classify_dealer_type(
            "Auto Service Center"
        )

    def test_deduplicate_dealers(self, data_cleaner, duplicate_dealers_list):
        """Test deduplication of dealer list."""
        unique_dealers = data_cleaner.deduplicate_dealers(duplicate_dealers_list)
        assert len(unique_dealers) == 2  # Should remove 1 duplicate

        # Check that unique dealers are preserved
        names = [d["name"] for d in unique_dealers]
        assert "ABC Toyota" in names
        assert "XYZ Honda" in names

    def test_deduplicate_dealers_with_no_duplicates(
        self, data_cleaner, sample_dealers_list
    ):
        """Test deduplication with no duplicates."""
        unique_dealers = data_cleaner.deduplicate_dealers(sample_dealers_list)
        assert len(unique_dealers) == len(sample_dealers_list)

    def test_deduplicate_dealers_case_insensitive(self, data_cleaner):
        """Test deduplication is case-insensitive."""
        dealers_with_case_duplicates = [
            {
                "name": "ABC Toyota",
                "street": "123 Main St",
                "city": "Boston",
                "state": "MA",
            },
            {
                "name": "abc toyota",  # Same but lowercase
                "street": "123 main st",
                "city": "boston",
                "state": "MA",
            },
        ]
        unique_dealers = data_cleaner.deduplicate_dealers(dealers_with_case_duplicates)
        assert len(unique_dealers) == 1


@pytest.mark.unit
class TestDataCleanerEdgeCases:
    """Test edge cases for DataCleaner."""

    def test_normalize_name_empty_string(self, data_cleaner):
        """Test normalization of empty name."""
        assert data_cleaner.normalize_name("") == ""

    def test_normalize_name_with_special_characters(self, data_cleaner):
        """Test normalization with special characters."""
        result = data_cleaner.normalize_name("Bob's Auto & Truck")
        assert "Bob's" in result or "Bobs" in result

    def test_extract_phone_number_no_phone(self, data_cleaner):
        """Test phone extraction with no phone number."""
        result = data_cleaner.extract_phone_number("No phone here")
        assert result == "" or result == "No phone here"

    def test_deduplicate_dealers_empty_list(self, data_cleaner):
        """Test deduplication with empty list."""
        unique_dealers = data_cleaner.deduplicate_dealers([])
        assert len(unique_dealers) == 0

    def test_is_valid_dealership_with_none_values(self, data_cleaner):
        """Test validation with None values."""
        invalid_dealer = {"name": None, "street": None, "city": None, "state": None}
        assert data_cleaner.is_valid_dealership(invalid_dealer) is False
