"""
Configuration settings for the Dealer Scraper application.
Centralizes all constants and environment-specific settings.
"""

import os
from dataclasses import dataclass, field
from typing import Set, List

@dataclass
class AppConfig:
    # Scraping Settings
    DEFAULT_TIMEOUT: int = 60000  # 60 seconds
    HEADLESS: bool = True
    VIEWPORT_WIDTH: int = 1920
    VIEWPORT_HEIGHT: int = 1080
    
    # User Agent Rotation
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Blocked Domains (Known to require Playwright/Stealth)
    KNOWN_BLOCKED_DOMAINS: Set[str] = field(default_factory=lambda: {
        "ancira.com",
        "albrechtauto.com",
        "allensamuels.com",
        "baliseauto.com",
        "bakermotorcompany.com",
        "bakerautogroup.com",
    })

    # Data Validation
    INVALID_NAMES: Set[str] = field(default_factory=lambda: {
        "locations", "saved", "community news", "essential cookies", 
        "sales", "service phone:", "parts phone:"
    })
    
    # Car Brands for Classification
    CAR_BRANDS: List[str] = field(default_factory=lambda: [
        "Acura", "Airstream", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", 
        "Bugatti", "Cadillac", "Chevrolet", "Ferrari", "FIAT", "Ford", "Genesis", "GMC", 
        "Honda", "Hummer", "Hyundai", "Infiniti", "Isuzu", "Jaguar", "Kia", "Lamborghini", 
        "Land Rover", "Lexus", "Lincoln", "Maserati", "Mazda", "McLaren", "Mercedes-Benz", 
        "Mini", "Mitsubishi", "Nissan", "Polestar", "Porsche", "Rolls-Royce", "smart", 
        "Sprinter", "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo", "Lotus", "INEOS", 
        "Koenigsegg", "Harley-Davidson", "Rimac", "Karma", "Lucid", "Vinfast", "CDJR", 
        "CDJRF", "Buick GMC", "Rivian", "Ford PRO", "GMC/Chevy Business Elite", 
        "RAM Commercial", "Freightliner", "Western Star", "International", "Peterbilt", 
        "Kenworth", "Mack", "Hino", "Capacity", "Autocar", "Fuso", "Maybach", "Pagani", 
        "Chrysler", "Dodge", "Scion", "Jeep"
    ])

    # Canadian Provinces
    CANADIAN_PROVINCES: Set[str] = field(default_factory=lambda: {
        "AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", 
        "ON", "PE", "QC", "SK", "YT"
    })

    # UI Settings
    PAGE_TITLE: str = "Dealer Location Scraper"
    PAGE_ICON: str = "🚗"

# Global Config Instance
config = AppConfig()
