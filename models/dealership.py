"""
Data models and validation for dealership information.

This module provides structured data models for dealership data
with validation and standardization capabilities.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import re
from config.settings import Constants


@dataclass
class DealershipData:
    """Structured representation of dealership information."""
    
    name: str = ""
    street: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    phone: str = ""
    website: str = ""
    dealer_group: str = ""
    dealership_type: str = ""
    car_brand: str = ""
    country: str = ""
    
    def __post_init__(self):
        """Post-initialization processing and validation."""
        self._standardize_fields()
        self._classify_dealership()
        self._set_country()
        self._extract_car_brands()
    
    def _standardize_fields(self):
        """Standardize and clean field values."""
        # Clean and title case name
        if self.name:
            self.name = self._apply_title_case_with_abbreviations(self.name)
        
        # Clean and standardize address
        if self.street:
            self.street = self._standardize_address(self.street)
        
        # Clean city
        if self.city:
            self.city = self.city.strip().title().rstrip(", ")
        
        # Uppercase state
        if self.state:
            self.state = self.state.strip().upper()
        
        # Clean website
        if self.website:
            self.website = self._clean_website(self.website)
    
    def _standardize_address(self, address: str) -> str:
        """Apply standard address abbreviations and formatting."""
        # Apply abbreviations
        for pattern, replacement in Constants.ADDRESS_ABBREVIATIONS.items():
            address = re.sub(pattern, replacement, address, flags=re.IGNORECASE)
        
        # Convert to title case
        address = address.title()
        
        # Restore uppercase abbreviations
        for abbr in Constants.UPPERCASE_ABBREVIATIONS:
            pattern = rf"\b{abbr.title()}(?=\b|[.,;:!?\s]|$)"
            address = re.sub(pattern, abbr, address)
        
        # Remove trailing punctuation and spaces
        address = re.sub(r"[.,\s]+$", "", address)
        
        return address
    
    def _apply_title_case_with_abbreviations(self, text: str) -> str:
        """Apply title case while preserving uppercase abbreviations."""
        text = text.title()
        for abbr in Constants.UPPERCASE_ABBREVIATIONS:
            pattern = rf"\b{abbr.title()}(?=\b|[.,;:!?\s]|$)"
            text = re.sub(pattern, abbr, text)
        return text
    
    def _clean_website(self, website: str) -> str:
        """Clean and standardize website URLs."""
        # Remove protocol and www
        website = re.sub(r"^https?://(www\.)?", "", website)
        # Replace backslashes with forward slashes  
        website = re.sub(r"\\+", "/", website)
        # Remove trailing slashes
        website = website.rstrip("/")
        return website
    
    def _classify_dealership(self):
        """Classify dealership type based on name."""
        if not self.dealership_type and self.name:
            name_lower = self.name.lower()
            
            # Check for collision
            if any(keyword in name_lower for keyword in Constants.COLLISION_KEYWORDS):
                self.dealership_type = 'Collision'
            # Check for fixed ops/service
            elif any(keyword in name_lower for keyword in Constants.FIXED_OPS_KEYWORDS):
                self.dealership_type = 'Fixed Ops'
            # Check for used car center
            elif any(keyword in name_lower for keyword in Constants.USED_CAR_KEYWORDS):
                self.dealership_type = 'Used'
            # Check for franchised (has brand name)
            elif any(brand.lower() in name_lower for brand in Constants.CAR_BRANDS):
                self.dealership_type = 'Franchised'
            else:
                self.dealership_type = 'Unknown'
    
    def _set_country(self):
        """Set country based on state/province."""
        if not self.country and self.state:
            if self.state.strip() in Constants.CANADIAN_PROVINCES:
                self.country = "Canada"
            else:
                self.country = "United States of America"
    
    def _extract_car_brands(self):
        """Extract car brands from dealership name."""
        if not self.car_brand and self.name:
            name_lower = self.name.lower()
            
            # Check for special multi-brand combinations
            if all(word in name_lower for word in ['chrysler', 'jeep', 'dodge', 'ram', 'fiat']):
                self.car_brand = 'CDJRF'
            elif all(word in name_lower for word in ['chrysler', 'jeep', 'dodge', 'ram']):
                self.car_brand = 'CDJR'
            else:
                # Find individual brands
                found_brands = [brand for brand in Constants.CAR_BRANDS 
                              if brand.lower() in name_lower]
                if found_brands:
                    self.car_brand = "; ".join(found_brands)
    
    def is_valid(self) -> bool:
        """Check if dealership data is valid."""
        # Must have name (street address is optional)
        if not self.name:
            return False
        
        # Check for invalid names
        name_lower = self.name.lower()
        if name_lower in Constants.INVALID_DEALERSHIP_NAMES:
            return False
        
        # Check for invalid websites
        if self.website and (self.website.startswith("#") or self.website.startswith("/")):
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary with standardized column names."""
        return {
            "Dealership": self.name,
            "Dealer Group": self.dealer_group,
            "Dealership Type": self.dealership_type,
            "Car Brand": self.car_brand,
            "Address": self.street,
            "City": self.city,
            "State/Province": self.state,
            "Postal Code": self.zip_code,
            "Phone": self.phone,
            "Country": self.country,
            "Website": self.website
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], dealer_group: str = "", page_url: str = "") -> 'DealershipData':
        """Create DealershipData from dictionary."""
        return cls(
            name=data.get("name", ""),
            street=data.get("street", ""),
            city=data.get("city", ""),
            state=data.get("state", ""),
            zip_code=data.get("zip", ""),
            phone=data.get("phone", ""),
            website=data.get("website", page_url),
            dealer_group=dealer_group
        )


class DealershipCollection:
    """Collection of dealerships with deduplication and validation."""
    
    def __init__(self):
        self.dealerships: List[DealershipData] = []
        self._seen_keys = set()
    
    def add(self, dealership: DealershipData) -> bool:
        """Add dealership if valid and not duplicate."""
        if not dealership.is_valid():
            return False
        
        # Create deduplication key
        key = self._create_dedup_key(dealership)
        if key in self._seen_keys:
            return False
        
        self.dealerships.append(dealership)
        self._seen_keys.add(key)
        return True
    
    def _create_dedup_key(self, dealership: DealershipData) -> tuple:
        """Create key for deduplication based on name and street."""
        name_norm = re.sub(r'\s+', ' ', dealership.name or '').strip().lower()
        street_norm = re.sub(r'\s+', ' ', dealership.street or '').strip().lower()
        return (name_norm, street_norm)
    
    def extend(self, dealerships: List[DealershipData]):
        """Add multiple dealerships."""
        for dealership in dealerships:
            self.add(dealership)
    
    def to_dict_list(self) -> List[Dict[str, str]]:
        """Convert all dealerships to list of dictionaries."""
        return [d.to_dict() for d in self.dealerships]
    
    def __len__(self) -> int:
        return len(self.dealerships)
    
    def __iter__(self):
        return iter(self.dealerships)