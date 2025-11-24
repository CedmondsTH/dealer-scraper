"""
Address parsing utilities for dealer location extraction.

This module provides functions to parse and normalize address data
from various dealer website formats.
"""

import re
from typing import Tuple


class AddressParser:
    """Handles parsing of address strings into components."""
    
    def __init__(self):
        # Regex patterns for US and Canadian postal codes
        self.us_zip_pattern = r"\d{5}(?:-\d{4})?"
        self.canadian_postal_pattern = r"[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d"
        
        # Canadian provinces for validation
        self.canadian_provinces = {
            "AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", 
            "ON", "PE", "QC", "SK", "YT"
        }
    
    def parse_address(self, address_text: str) -> Tuple[str, str, str, str]:
        """
        Parses a combined address string into street, city, state/province, and postal code.
        Handles both US (ZIP code) and Canadian (Postal Code) formats.
        
        Args:
            address_text: Raw address string to parse
            
        Returns:
            Tuple of (street, city, state, postal_code)
        """
        if not address_text:
            return "", "", "", ""
            
        street, city, state, postal_code = "", "", "", ""

        # Try Pattern 1: Street, City, State ZIP, Country 
        # e.g., "222 W Merchandise Mart Plaza, Chicago, IL 60654, USA"
        pattern1 = re.compile(
            r"^(.*?),\s*([^,]+?),\s*([A-Z]{2})\s+(" + 
            self.us_zip_pattern + "|" + self.canadian_postal_pattern + 
            r")(?:,\s*[^,]+)?\s*$"
        )
        match = pattern1.match(address_text)
        if match:
            street = match.group(1).strip()
            city = match.group(2).strip()
            state = match.group(3).strip().upper()
            postal_code = match.group(4).strip()
            postal_code = self._format_canadian_postal_code(postal_code)
            return street, city, state, postal_code
        
        # Try Pattern 2: Street, City, State ZIP (without country)
        pattern2 = re.compile(
            r"^(.*?),\s*([^,]+?),\s*([A-Za-z]{2})\s+(" + 
            self.us_zip_pattern + "|" + self.canadian_postal_pattern + 
            r")\s*$"
        )
        match = pattern2.match(address_text)
        if match:
            street = match.group(1).strip()
            city = match.group(2).strip()
            state = match.group(3).strip().upper()
            postal_code = match.group(4).strip()
            postal_code = self._format_canadian_postal_code(postal_code)
            return street, city, state, postal_code
        
        # Fallback for less structured addresses
        return self._parse_fallback(address_text)
    
    def _format_canadian_postal_code(self, postal_code: str) -> str:
        """Ensures Canadian postal codes have proper spacing."""
        if re.match(self.canadian_postal_pattern, postal_code) and ' ' not in postal_code:
            return postal_code[:3] + ' ' + postal_code[3:]
        return postal_code
    
    def _parse_fallback(self, address_text: str) -> Tuple[str, str, str, str]:
        """Fallback parsing for less structured addresses."""
        parts = [part.strip() for part in address_text.split(',') if part.strip()]
        if len(parts) < 3:
            return "", "", "", ""
            
        street = parts[0]
        city = parts[1]
        
        # Handle the last part which might be "IL 60654" or "IL 60654 USA"
        last_parts = parts[-1].strip().split()
        if len(parts) >= 4 and len(last_parts) == 1:
            # Format: Street, City, State, ZIP, Country
            state = parts[2].strip().upper()
            postal_code = parts[3].strip()
        else:
            # Format: Street, City, "IL 60654" or "IL 60654 USA"
            if len(last_parts) >= 2:
                state = last_parts[0].strip().upper()
                postal_code = last_parts[1].strip()
            else:
                # Try regex extraction from the last part
                last_part = parts[-1]
                state, postal_code = self._extract_state_zip_regex(last_part)
        
        return street, city, state, postal_code
    
    def _extract_state_zip_regex(self, text: str) -> Tuple[str, str]:
        """Extract state and postal code using regex patterns."""
        # Try Canadian postal code pattern first
        m_can = re.search(r"([A-Z]{2})\s+(" + self.canadian_postal_pattern + r")", text)
        if m_can:
            return m_can.group(1), m_can.group(2)
            
        # Try US ZIP code pattern
        m_us = re.search(r"([A-Z]{2})\s+(" + self.us_zip_pattern + r")", text)
        if m_us:
            return m_us.group(1), m_us.group(2)
            
        return "", ""
    
    def is_canadian_province(self, state_code: str) -> bool:
        """Check if a state code is a Canadian province."""
        return state_code.strip().upper() in self.canadian_provinces
    
    def normalize_address_abbreviations(self, address: str) -> str:
        """Standardize common address abbreviations."""
        if not address:
            return ""
            
        # Apply common abbreviations
        abbreviations = {
            r"\bStreet\b": "St",
            r"\bAvenue\b": "Ave", 
            r"\bBoulevard\b": "Blvd",
            r"\bHighway\b": "Hwy",
            r"\bLane\b": "Ln",
            r"\bDrive\b": "Dr",
            r"\bRoad\b": "Rd",
            r"\bParkway\b": "Pkwy",
            r"\bExpressway\b": "Expy"
        }
        
        normalized = address
        for pattern, replacement in abbreviations.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        # Convert to title case
        normalized = normalized.title()
        
        # Restore common abbreviations to uppercase
        uppercase_abbrevs = ["NE", "NW", "SE", "SW", "GMC", "FIAT", "RAM", "BMW", "USA", "II", "III", "IV"]
        for abbr in uppercase_abbrevs:
            pattern = rf"\b{abbr.title()}(?=\b|[.,;:!?\s]|$)"
            normalized = re.sub(pattern, abbr, normalized)
        
        # Remove trailing punctuation and spaces
        normalized = re.sub(r"[.,\s]+$", "", normalized)
        
        return normalized


# Create singleton instance for easy importing
address_parser = AddressParser()

# Convenience function for backward compatibility
def parse_address(address_text: str) -> Tuple[str, str, str, str]:
    """Parse address string into components."""
    return address_parser.parse_address(address_text)