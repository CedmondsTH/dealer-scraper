import sys
import os
from pathlib import Path
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Dealer
from src.utils.data_cleaner import data_cleaner

def test_dealer_model_validation():
    """Test that Dealer model validates data correctly."""
    valid_data = {
        "Dealership": "Test Motors",
        "Dealer Group": "Test Group",
        "Dealership Type": "Franchised",
        "Car Brand": "Toyota",
        "Address": "123 Main St",
        "City": "Test City",
        "State/Province": "TX",
        "Postal Code": "75001",
        "Phone": "555-0123",
        "Country": "United States of America",
        "Website": "https://example.com"
    }
    
    dealer = Dealer(**valid_data)
    assert dealer.name == "Test Motors"
    assert dealer.state == "TX"
    assert dealer.website == "https://example.com"

def test_dealer_model_missing_fields():
    """Test that Dealer model raises error for missing required fields."""
    invalid_data = {
        "Dealership": "Test Motors"
        # Missing other required fields
    }
    
    with pytest.raises(ValueError):
        Dealer(**invalid_data)

def test_data_cleaner_normalization():
    """Test data cleaner normalization functions."""
    assert data_cleaner.normalize_name("test motors llc") == "Test Motors LLC"
    assert data_cleaner.normalize_city("new york, ") == "New York"
    assert data_cleaner.normalize_website("https://www.example.com/") == "example.com"
