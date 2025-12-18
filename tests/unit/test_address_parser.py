"""
Unit tests for address_parser module.
"""

import pytest

from src.utils.address_parser import AddressParser, parse_address


class TestAddressParser:
    """Test suite for address parsing functionality."""

    def test_parse_us_address_standard_format(self):
        """Test parsing standard US address."""
        address = "123 Main St, Boston, MA 02101"
        street, city, state, zip_code = parse_address(address)

        assert street == "123 Main St"
        assert city == "Boston"
        assert state == "MA"
        assert zip_code == "02101"

    def test_parse_us_address_with_country(self):
        """Test parsing US address with country suffix."""
        address = "456 Oak Ave, Cambridge, MA 02139, USA"
        street, city, state, zip_code = parse_address(address)

        assert street == "456 Oak Ave"
        assert city == "Cambridge"
        assert state == "MA"
        assert zip_code == "02139"

    def test_parse_canadian_address(self):
        """Test parsing Canadian address."""
        address = "789 Maple Rd, Toronto, ON M5H 2N2"
        street, city, state, zip_code = parse_address(address)

        assert street == "789 Maple Rd"
        assert city == "Toronto"
        assert state == "ON"
        assert zip_code == "M5H 2N2"

    def test_parse_canadian_address_with_country(self):
        """Test parsing Canadian address with country."""
        address = "321 Elm St, Vancouver, BC V6B 4Y8, Canada"
        street, city, state, zip_code = parse_address(address)

        assert street == "321 Elm St"
        assert city == "Vancouver"
        assert state == "BC"
        assert zip_code == "V6B 4Y8"

    def test_parse_address_with_suite_number(self):
        """Test parsing address with suite number."""
        address = "100 Tech Dr Suite 200, San Francisco, CA 94105"
        street, city, state, zip_code = parse_address(address)

        assert "100 Tech Dr" in street
        assert "Suite 200" in street or "suite 200" in street.lower()
        assert city == "San Francisco"
        assert state == "CA"

    def test_parse_address_pipe_separator(self):
        """Test parsing address with pipe separator."""
        address = "1305 Gray St. | Houston, TX 77002"
        street, city, state, zip_code = parse_address(address)

        assert "1305 Gray St" in street
        assert city == "Houston"
        assert state == "TX"
        assert zip_code == "77002"

    def test_parse_address_with_extra_whitespace(self):
        """Test parsing address with extra whitespace."""
        address = "  555  Main  St  ,  Boston  ,  MA  02101  "
        street, city, state, zip_code = parse_address(address)

        assert street.strip()
        assert city == "Boston"
        assert state == "MA"
        assert zip_code == "02101"

    def test_parse_address_extended_zip(self):
        """Test parsing address with extended ZIP code."""
        address = "200 Park Ave, New York, NY 10166-0005"
        street, city, state, zip_code = parse_address(address)

        assert street == "200 Park Ave"
        assert city == "New York"
        assert state == "NY"
        assert "10166" in zip_code

    def test_parse_address_empty_string(self):
        """Test parsing empty address string."""
        street, city, state, zip_code = parse_address("")

        assert street == ""
        assert city == ""
        assert state == ""
        assert zip_code == ""

    def test_parse_address_missing_components(self):
        """Test parsing incomplete address."""
        address = "123 Main St"
        street, city, state, zip_code = parse_address(address)

        # Should handle gracefully, returning what it can
        assert street or city or state or zip_code is not None


@pytest.mark.unit
class TestAddressParserEdgeCases:
    """Test edge cases for address parsing."""

    def test_parse_address_with_po_box(self):
        """Test parsing PO Box address."""
        address = "PO Box 1234, Springfield, IL 62701"
        street, city, state, zip_code = parse_address(address)

        assert "PO Box" in street or "P.O. Box" in street
        assert city == "Springfield"
        assert state == "IL"

    def test_parse_address_with_directions(self):
        """Test parsing address with cardinal directions."""
        address = "1000 N Main St, Phoenix, AZ 85004"
        street, city, state, zip_code = parse_address(address)

        assert "1000" in street
        assert "Main St" in street
        assert city == "Phoenix"

    def test_parse_address_multiline(self):
        """Test parsing multiline address."""
        address = "500 Tech Center\\nSuite 100\\nDallas, TX 75201"
        street, city, state, zip_code = parse_address(address)

        # Should handle newlines or at least not crash
        assert street or city or state or zip_code

    def test_parse_address_international_format(self):
        """Test parsing non-US/Canada address (best effort)."""
        address = "10 Downing Street, London, UK SW1A 2AA"
        street, city, state, zip_code = parse_address(address)

        # Should handle gracefully, may not extract perfectly
        assert street or city or state or zip_code

    def test_parse_address_with_special_characters(self):
        """Test parsing address with special characters."""
        address = "1234 O'Brien St., McLean, VA 22102"
        street, city, state, zip_code = parse_address(address)

        assert "1234" in street
        assert "McLean" in city or "Mclean" in city
        assert state == "VA"

    def test_parse_address_rural_route(self):
        """Test parsing rural route address."""
        address = "RR 1 Box 123, Smalltown, KS 67890"
        street, city, state, zip_code = parse_address(address)

        assert "RR" in street or "Box" in street
        assert city
        assert state == "KS"
