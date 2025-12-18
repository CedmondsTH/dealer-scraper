"""
Centralized configuration management for the Dealer Scraper application.

This module consolidates all configuration settings, environment variables,
and application constants into a single source of truth.
"""

import os
import logging
from typing import Set, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, will use system environment variables only
    pass


@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations."""
    timeout: int = int(os.getenv('SCRAPING_TIMEOUT', '60000'))
    headless: bool = os.getenv('SCRAPING_HEADLESS', 'true').lower() == 'true'
    viewport_width: int = int(os.getenv('SCRAPING_VIEWPORT_WIDTH', '1920'))
    viewport_height: int = int(os.getenv('SCRAPING_VIEWPORT_HEIGHT', '1080'))
    max_retries: int = int(os.getenv('SCRAPING_MAX_RETRIES', '3'))
    debug_files: bool = os.getenv('SCRAPING_DEBUG_FILES', 'false').lower() == 'true'
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class DataConfig:
    """Configuration for data processing."""
    max_dealers: int = int(os.getenv('DATA_MAX_DEALERS', '1000'))
    min_name_length: int = int(os.getenv('DATA_MIN_NAME_LENGTH', '2'))
    validate_addresses: bool = os.getenv('DATA_VALIDATE_ADDRESSES', 'true').lower() == 'true'


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = os.getenv('LOG_LEVEL', 'INFO')
    file_path: Optional[str] = os.getenv('LOG_FILE_PATH') or None
    max_file_size: int = int(os.getenv('LOG_MAX_FILE_SIZE', '10485760'))  # 10MB
    backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    @property
    def level_value(self) -> int:
        """Convert string log level to logging constant."""
        return getattr(logging, self.level.upper(), logging.INFO)


@dataclass
class UIConfig:
    """Configuration for user interface."""
    page_title: str = os.getenv('UI_PAGE_TITLE', 'Dealer Group Dealership Scraper')
    layout: str = os.getenv('UI_LAYOUT', 'centered')
    logo_path: str = os.getenv('UI_LOGO_PATH', 'assets/trackhawk_logo.png')
    cache_enabled: bool = os.getenv('UI_CACHE_ENABLED', 'true').lower() == 'true'


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # Environment
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    environment: str = os.getenv('ENVIRONMENT', 'production')
    
    # API Keys
    gemini_api_key: str = os.getenv('GEMINI_API_KEY', '')
    
    # Sub-configurations
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    # Known blocked domains (require Playwright)
    blocked_domains: Set[str] = field(default_factory=lambda: {
        "ancira.com",
        "albrechtauto.com",
        "allensamuels.com",
        "baliseauto.com",
        "bakermotorcompany.com",
        "bakerautogroup.com",
    })
    
    def validate(self) -> None:
        """Validate required configuration."""
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
    
    def __post_init__(self):
        """Initialize sub-configurations if not already set."""
        if not isinstance(self.scraping, ScrapingConfig):
            self.scraping = ScrapingConfig()
        if not isinstance(self.data, DataConfig):
            self.data = DataConfig()
        if not isinstance(self.logging, LoggingConfig):
            self.logging = LoggingConfig()
        if not isinstance(self.ui, UIConfig):
            self.ui = UIConfig()


class Constants:
    """Application constants and static data."""
    
    # Supported car brands for classification
    CAR_BRANDS: List[str] = [
        "Acura", "Airstream", "Alfa Romeo", "Aston Martin", "Audi", "Bentley",
        "BMW", "Bugatti", "Buick", "Cadillac", "Chevrolet", "Chrysler", "Dodge",
        "Ferrari", "FIAT", "Ford", "Genesis", "GMC", "Honda", "Hummer", "Hyundai",
        "Infiniti", "Isuzu", "Jaguar", "Jeep", "Kia", "Lamborghini", "Land Rover",
        "Lexus", "Lincoln", "Maserati", "Mazda", "McLaren", "Mercedes-Benz", "Mini",
        "Mitsubishi", "Nissan", "Polestar", "Porsche", "RAM", "Rolls-Royce", "Scion",
        "smart", "Sprinter", "Subaru", "Tesla", "Toyota", "Volkswagen", "Volvo",
        "Lotus", "INEOS", "Koenigsegg", "Harley-Davidson", "Rimac", "Karma", "Lucid",
        "Vinfast", "CDJR", "CDJRF", "Buick GMC", "Rivian", "Ford PRO",
        "GMC/Chevy Business Elite", "RAM Commercial", "Freightliner", "Western Star",
        "International", "Peterbilt", "Kenworth", "Mack", "Hino", "Capacity",
        "Autocar", "Fuso", "Maybach", "Pagani"
    ]
    
    # Canadian provinces for country classification
    CANADIAN_PROVINCES: Set[str] = {
        "AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU",
        "ON", "PE", "QC", "SK", "YT"
    }
    
    # Dealership type keywords
    COLLISION_KEYWORDS: List[str] = [
        'collision', 'body shop', 'autobody', 'auto body', 'repair center',
        'collision repair', 'body repair', 'repair'
    ]
    
    FIXED_OPS_KEYWORDS: List[str] = [
        'service', 'quick lane', 'express', 'maintenance', 'tire', 'lube'
    ]
    
    USED_CAR_KEYWORDS: List[str] = [
        'used', 'pre-owned', 'auto sales', 'car sales'
    ]
    
    # Invalid dealership names (for filtering)
    INVALID_DEALERSHIP_NAMES: Set[str] = {
        "locations", "saved", "community news", "essential cookies",
        "sales", "service phone:", "parts phone:"
    }
    
    # Address standardization patterns
    ADDRESS_ABBREVIATIONS: dict = {
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
    UPPERCASE_ABBREVIATIONS: List[str] = [
        "NE", "NW", "SE", "SW", "GMC", "FIAT", "RAM", "BMW", "USA",
        "II", "III", "IV", "LLC", "INC", "LTD", "LP", "PC"
    ]
    
    # Directory page patterns for link extraction
    DIRECTORY_PATTERNS: List[str] = [
        "/locations/", "/dealers/", "/store-locations", "state=", "/by-",
        "/find-", "/inventory/", "/location/", "/our-locations", "/search/"
    ]
    
    # Standard output column order
    OUTPUT_COLUMNS: List[str] = [
        "Dealership", "Dealer Group", "Dealership Type", "Car Brand",
        "Address", "City", "State/Province", "Postal Code", "Phone",
        "Country", "Website"
    ]


# Global configuration instance
config = AppConfig()


def setup_logging() -> None:
    """Configure application-wide logging."""
    log_config = config.logging
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_config.level_value)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_config.level_value)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if configured)
    if log_config.file_path:
        from logging.handlers import RotatingFileHandler
        
        # Ensure log directory exists
        log_path = Path(log_config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_config.file_path,
            maxBytes=log_config.max_file_size,
            backupCount=log_config.backup_count
        )
        file_handler.setLevel(log_config.level_value)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


# Initialize logging on module import
setup_logging()

