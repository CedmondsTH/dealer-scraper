"""
Configuration management for the Dealership Scraper application.

This module handles all configuration settings, environment variables,
and application constants in a centralized, secure manner.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class for the application."""
    
    # API Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    
    # Scraping Configuration
    PLAYWRIGHT_TIMEOUT: int = int(os.getenv('PLAYWRIGHT_TIMEOUT', '60000'))
    MAX_DEALERSHIPS: int = int(os.getenv('MAX_DEALERSHIPS', '1000'))
    SCROLL_DELAY: int = int(os.getenv('SCROLL_DELAY', '1500'))
    
    # Application Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # File Configuration
    DEBUG_HTML_FILE: str = "debug_output.html"
    GEMINI_SUCCESS_LOG: str = "gemini_successes.csv"
    
    # Browser Configuration
    BROWSER_HEADLESS: bool = os.getenv('BROWSER_HEADLESS', 'True').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return True


class Constants:
    """Application constants and static data."""
    
    # Supported car brands for classification
    CAR_BRANDS = [
        "Acura", "Airstream", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", 
        "BMW", "Bugatti", "Cadillac", "Chevrolet", "Ferrari", "FIAT", "Ford", 
        "Genesis", "GMC", "Honda", "Hummer", "Hyundai", "Infiniti", "Isuzu", 
        "Jaguar", "Kia", "Lamborghini", "Land Rover", "Lexus", "Lincoln", 
        "Maserati", "Mazda", "McLaren", "Mercedes-Benz", "Mini", "Mitsubishi", 
        "Nissan", "Polestar", "Porsche", "Rolls-Royce", "smart", "Sprinter", 
        "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo", "Lotus", "INEOS", 
        "Koenigsegg", "Harley-Davidson", "Rimac", "Karma", "Lucid", "Vinfast",
        "CDJR", "CDJRF", "Buick GMC", "Rivian", "Ford PRO", "GMC/Chevy Business Elite", 
        "RAM Commercial", "Freightliner", "Western Star", "International", "Peterbilt", 
        "Kenworth", "Mack", "Hino", "Capacity", "Autocar", "Fuso", "Maybach",
        "Pagani", "Chrysler", "Dodge", "Scion", "Jeep"
    ]
    
    # Canadian provinces for country classification
    CANADIAN_PROVINCES = {
        "AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"
    }
    
    # Dealership type keywords
    COLLISION_KEYWORDS = [
        'collision', 'body shop', 'autobody', 'auto body', 'repair center', 
        'collision repair', 'body repair', 'repair'
    ]
    
    FIXED_OPS_KEYWORDS = [
        'service', 'quick lane', 'express', 'maintenance', 'tire', 'lube'
    ]
    
    USED_CAR_KEYWORDS = [
        'used', 'pre-owned', 'auto sales', 'car sales'
    ]
    
    # Invalid dealership names (for filtering)
    INVALID_DEALERSHIP_NAMES = {
        "locations", "saved", "community news", "essential cookies", 
        "sales", "service phone:", "parts phone:"
    }
    
    # Address standardization patterns
    ADDRESS_ABBREVIATIONS = {
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
    
    # Common uppercase abbreviations
    UPPERCASE_ABBREVIATIONS = [
        "NE", "NW", "SE", "SW", "GMC", "FIAT", "RAM", "BMW", "USA", "II", "III", "IV"
    ]
    
    # Directory page patterns for link extraction
    DIRECTORY_PATTERNS = [
        "/locations/", "/dealers/", "/store-locations", "state=", "/by-", 
        "/find-", "/inventory/", "/location/", "/our-locations", "/search/"
    ]
    
    # Standard output column order
    OUTPUT_COLUMNS = [
        "Dealership", "Dealer Group", "Dealership Type", "Car Brand", 
        "Address", "City", "State/Province", "Postal Code", "Phone", 
        "Country", "Website"
    ]


# Create global config instance
config = Config()