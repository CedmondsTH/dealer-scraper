"""
Unit tests for address parsing functionality.

Tests the AddressParser utility to ensure accurate parsing
of various address formats from dealer websites.
"""

import pytest
from utils.address_parser import AddressParser, parse_address


class TestAddressParser:
    """Test cases for the AddressParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = AddressParser()
    
    def test_us_address_with_country(self):
        """Test parsing US address with country suffix."""
        address = "222 W Merchandise Mart Plaza, Chicago, IL 60654, USA"
        street, city, state, zip_code = self.parser.parse_address(address)
        
        assert street == "222 W Merchandise Mart Plaza"
        assert city == "Chicago"
        assert state == "IL"
        assert zip_code == "60654"
    
    def test_us_address_without_country(self):
        """Test parsing US address without country."""
        address = "123 Main Street, Anytown, CA 90210"
        street, city, state, zip_code = self.parser.parse_address(address)
        
        assert street == "123 Main Street"
        assert city == "Anytown"
        assert state == "CA"
        assert zip_code == "90210"
    
    def test_canadian_address(self):
        """Test parsing Canadian address with postal code."""
        address = "123 Maple St, Toronto, ON M5V 3A1, Canada"
        street, city, state, zip_code = self.parser.parse_address(address)
        
        assert street == "123 Maple St"
        assert city == "Toronto"
        assert state == "ON"
        assert zip_code == "M5V 3A1"
    
    def test_canadian_postal_code_formatting(self):
        """Test Canadian postal code gets proper spacing."""
        # Test without space
        result = self.parser._format_canadian_postal_code("M5V3A1")
        assert result == "M5V 3A1"
        
        # Test with space (should remain unchanged)
        result = self.parser._format_canadian_postal_code("M5V 3A1")
        assert result == "M5V 3A1"
    
    def test_empty_address(self):
        """Test handling of empty address."""
        street, city, state, zip_code = self.parser.parse_address("")
        
        assert street == ""
        assert city == ""
        assert state == ""
        assert zip_code == ""
    
    def test_malformed_address(self):
        """Test handling of malformed address."""
        address = "Just some random text"
        street, city, state, zip_code = self.parser.parse_address(address)
        
        # Should return empty components for malformed address
        assert street == ""
        assert city == ""
        assert state == ""
        assert zip_code == ""
    
    def test_is_canadian_province(self):
        """Test Canadian province detection."""
        assert self.parser.is_canadian_province("ON") is True
        assert self.parser.is_canadian_province("BC") is True
        assert self.parser.is_canadian_province("CA") is False  # US state
        assert self.parser.is_canadian_province("TX") is False  # US state
    
    def test_normalize_address_abbreviations(self):
        """Test address abbreviation normalization."""
        address = "123 Main Street, Downtown Avenue"
        result = self.parser.normalize_address_abbreviations(address)
        
        assert "St" in result
        assert "Ave" in result
        assert "Street" not in result
        assert "Avenue" not in result
    
    def test_convenience_function(self):
        """Test the convenience parse_address function."""
        address = "456 Oak Drive, Springfield, IL 62701"
        street, city, state, zip_code = parse_address(address)
        
        assert street == "456 Oak Drive"
        assert city == "Springfield"
        assert state == "IL"
        assert zip_code == "62701"


if __name__ == "__main__":
    pytest.main([__file__])