"""
Data cleaning and validation utilities for dealer information.

This module provides functions to clean, validate, and normalize
dealer data extracted from various websites.
"""

import re
import logging
from typing import Dict, List, Any

from config import Constants

logger = logging.getLogger(__name__)


class DataCleaner:
    """Handles cleaning and validation of dealer data."""
    
    def __init__(self):
        # Names that should be filtered out as invalid dealerships
        self.invalid_names = Constants.INVALID_DEALERSHIP_NAMES
        
        # Car brands for classification
        self.car_brands = Constants.CAR_BRANDS
        
        # Canadian provinces
        self.canadian_provinces = Constants.CANADIAN_PROVINCES
    
    def is_valid_dealership(self, dealer_data: Dict[str, Any]) -> bool:
        """
        Validate if a dealer record represents a legitimate dealership.
        
        Args:
            dealer_data: Dictionary containing dealer information
            
        Returns:
            True if valid dealership, False otherwise
        """
        # Handle both capitalized and lowercase key formats
        name = (dealer_data.get("name", "") or dealer_data.get("Name", "") or "").strip().lower()
        street = (dealer_data.get("street", "") or dealer_data.get("Street", "") or "").strip()
        website = (dealer_data.get("website", "") or dealer_data.get("Website", "") or "").strip()
        
        # Must have name and street
        if not name or not street:
            logger.debug(f"Invalid dealer: missing name or street")
            return False
        
        # Filter out invalid names
        if name in self.invalid_names:
            logger.debug(f"Invalid dealer: name '{name}' in invalid names list")
            return False
            
        # Filter out descriptive text that's not a dealer name
        if len(name) > 80 or any(phrase in name for phrase in [
            'treat', 'need', 'customer', 'concern', 'expectation', 'standard', 'demonstrate',
            'about', 'welcome to', 'group description', 'our mission'
        ]):
            logger.debug(f"Invalid dealer: name '{name}' appears to be descriptive text")
            return False
            
        # Filter out mangled addresses in street field
        if len(street) > 100 or ('directions' in street.lower() and ',' in street):
            logger.debug(f"Invalid dealer: mangled address in street field")
            return False
        
        # Filter out invalid websites
        if website.startswith("#") or website.startswith("/"):
            logger.debug(f"Invalid dealer: invalid website format")
            return False
        
        return True
    
    def normalize_name(self, name: str) -> str:
        """Normalize dealer name with proper capitalization."""
        if not name:
            return ""
        
        # Convert to title case
        normalized = name.strip().title()
        
        # Restore common abbreviations to uppercase
        uppercase_abbrevs = ["NE", "NW", "SE", "SW", "GMC", "FIAT", "RAM", "BMW", "USA", "II", "III", "IV", "LLC", "INC", "LTD"]
        for abbr in uppercase_abbrevs:
            pattern = rf"\b{abbr.title()}(?=\b|[.,;:!?\s]|$)"
            normalized = re.sub(pattern, abbr, normalized)
        
        return normalized
    
    def normalize_city(self, city: str) -> str:
        """Normalize city name."""
        if not city:
            return ""
        
        normalized = city.strip().title()
        # Remove trailing commas and spaces
        normalized = normalized.rstrip(", ")
        return normalized
    
    def normalize_website(self, website: str) -> str:
        """Normalize website URL."""
        if not website:
            return ""
        
        # Remove protocol and www prefix
        normalized = re.sub(r"^https?://(www\.)?", "", website)
        
        # Replace backslashes with forward slashes
        normalized = re.sub(r"\\+", "/", normalized)
        
        # Remove trailing slashes
        normalized = normalized.rstrip("/")
        
        return normalized
    
    def extract_phone_number(self, text: str) -> str:
        """Extract phone number from text."""
        if not text:
            return ""
        
        # Look for phone number patterns
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group() if match else ""
    
    def classify_dealer_type(self, name: str) -> str:
        """
        Classify dealer type based on name.
        
        Args:
            name: Dealer name to classify
            
        Returns:
            One of: 'Collision', 'Fixed Ops', 'Used', 'Franchised', 'Unknown'
        """
        if not name:
            return 'Unknown'
        
        name_lower = name.lower()
        
        # Collision
        collision_keywords = [
            'collision', 'body shop', 'autobody', 'auto body', 'repair center', 
            'collision repair', 'body repair', 'repair'
        ]
        if any(word in name_lower for word in collision_keywords):
            return 'Collision'
        
        # Fixed Ops / Service
        service_keywords = [
            'service', 'quick lane', 'express', 'maintenance', 'tire', 'lube'
        ]
        if any(word in name_lower for word in service_keywords):
            return 'Fixed Ops'
        
        # Used Car Center
        used_keywords = ['used', 'pre-owned', 'auto sales', 'car sales']
        if any(word in name_lower for word in used_keywords):
            return 'Used'
        
        # Franchised (check for car brands)
        if any(brand.lower() in name_lower for brand in self.car_brands):
            return 'Franchised'
        
        return 'Unknown'
    
    def extract_car_brands(self, name: str) -> str:
        """
        Extract car brands from dealer name.
        
        Args:
            name: Dealer name to analyze
            
        Returns:
            Semicolon-separated string of found brands
        """
        if not name:
            return ""
        
        name_lower = name.lower()
        
        # Check for CDJRF (Chrysler, Jeep, Dodge, Ram, FIAT)
        if all(word in name_lower for word in ['chrysler', 'jeep', 'dodge', 'ram', 'fiat']):
            return 'CDJRF'
        
        # Check for CDJR (Chrysler, Jeep, Dodge, Ram)
        if all(word in name_lower for word in ['chrysler', 'jeep', 'dodge', 'ram']):
            return 'CDJR'
        
        # Find individual brands
        found_brands = [brand for brand in self.car_brands if brand.lower() in name_lower]
        
        return "; ".join(found_brands) if found_brands else ""
    
    def determine_country(self, state_province: str) -> str:
        """
        Determine country based on state/province code.
        
        Args:
            state_province: State or province code
            
        Returns:
            'Canada' or 'United States of America'
        """
        if not state_province:
            return "United States of America"
        
        return "Canada" if state_province.strip().upper() in self.canadian_provinces else "United States of America"
    
    def deduplicate_dealers(self, dealers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate dealer entries based on normalized name and street.
        
        Args:
            dealers: List of dealer dictionaries
            
        Returns:
            Deduplicated list of dealers
        """
        def normalize_for_comparison(text: str) -> str:
            """Normalize text for comparison purposes."""
            return re.sub(r'\s+', ' ', (text or '').strip().lower())
        
        unique_dealers = []
        seen_keys = set()
        
        for dealer in dealers:
            name_norm = normalize_for_comparison(dealer.get('name', ''))
            street_norm = normalize_for_comparison(dealer.get('street', ''))
            city_norm = normalize_for_comparison(dealer.get('city', ''))
            
            # Create a more robust deduplication key
            if name_norm and street_norm:
                key = (name_norm, street_norm, city_norm)
                if key not in seen_keys:
                    unique_dealers.append(dealer)
                    seen_keys.add(key)
            elif name_norm and city_norm:
                # Fallback to name + city if no street
                key = (name_norm, '', city_norm)
                if key not in seen_keys:
                    unique_dealers.append(dealer)
                    seen_keys.add(key)
            else:
                # Keep entries missing name or key fields (they'll be filtered later)
                unique_dealers.append(dealer)
        
        return unique_dealers


# Create singleton instance for easy importing
data_cleaner = DataCleaner()