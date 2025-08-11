"""
Application settings and configuration.

This module provides centralized configuration management
with environment variable support and validation.
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class ScrapingSettings:
    """Settings for web scraping operations."""
    timeout: int = 60000
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    max_retries: int = 3
    retry_delay: int = 1
    enable_debug_files: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class DataSettings:
    """Settings for data processing operations."""
    max_dealers_per_site: int = 1000
    min_name_length: int = 2
    enable_address_validation: bool = True
    export_formats: list = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ['excel', 'csv']


@dataclass
class LoggingSettings:
    """Settings for logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class UISettings:
    """Settings for UI configuration."""
    page_title: str = "Dealer Group Dealership Scraper"
    page_icon: str = "🚗"
    layout: str = "centered"
    logo_path: str = "assets/trackhawk_logo.png"
    cache_enabled: bool = True


@dataclass
class Settings:
    """Main application settings."""
    scraping: ScrapingSettings
    data: DataSettings
    logging: LoggingSettings
    ui: UISettings
    
    # Environment
    debug: bool = False
    environment: str = "production"
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Create settings from environment variables."""
        
        # Scraping settings
        scraping = ScrapingSettings(
            timeout=int(os.getenv('SCRAPING_TIMEOUT', '60000')),
            headless=os.getenv('SCRAPING_HEADLESS', 'true').lower() == 'true',
            viewport_width=int(os.getenv('SCRAPING_VIEWPORT_WIDTH', '1920')),
            viewport_height=int(os.getenv('SCRAPING_VIEWPORT_HEIGHT', '1080')),
            max_retries=int(os.getenv('SCRAPING_MAX_RETRIES', '3')),
            enable_debug_files=os.getenv('SCRAPING_DEBUG_FILES', 'true').lower() == 'true'
        )
        
        # Data settings
        data = DataSettings(
            max_dealers_per_site=int(os.getenv('DATA_MAX_DEALERS', '1000')),
            min_name_length=int(os.getenv('DATA_MIN_NAME_LENGTH', '2')),
            enable_address_validation=os.getenv('DATA_VALIDATE_ADDRESSES', 'true').lower() == 'true'
        )
        
        # Logging settings
        log_file = os.getenv('LOG_FILE_PATH')
        if log_file:
            # Ensure log directory exists
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging_settings = LoggingSettings(
            level=os.getenv('LOG_LEVEL', 'INFO').upper(),
            file_path=log_file,
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', str(10 * 1024 * 1024))),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5'))
        )
        
        # UI settings
        ui = UISettings(
            page_title=os.getenv('UI_PAGE_TITLE', 'Dealer Group Dealership Scraper'),
            layout=os.getenv('UI_LAYOUT', 'centered'),
            logo_path=os.getenv('UI_LOGO_PATH', 'trackhawk_logo.png'),
            cache_enabled=os.getenv('UI_CACHE_ENABLED', 'true').lower() == 'true'
        )
        
        # Environment settings
        debug = os.getenv('DEBUG', 'false').lower() == 'true'
        environment = os.getenv('ENVIRONMENT', 'production')
        
        return cls(
            scraping=scraping,
            data=data,
            logging=logging_settings,
            ui=ui,
            debug=debug,
            environment=environment
        )
    
    def validate(self) -> None:
        """Validate settings and raise errors for invalid configurations."""
        
        # Validate scraping settings
        if self.scraping.timeout <= 0:
            raise ValueError("Scraping timeout must be positive")
        
        if self.scraping.viewport_width <= 0 or self.scraping.viewport_height <= 0:
            raise ValueError("Viewport dimensions must be positive")
        
        # Validate data settings
        if self.data.max_dealers_per_site <= 0:
            raise ValueError("Max dealers per site must be positive")
        
        if self.data.min_name_length <= 0:
            raise ValueError("Min name length must be positive")
        
        # Validate logging settings
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level not in valid_log_levels:
            raise ValueError(f"Log level must be one of {valid_log_levels}")
        
        # Validate UI settings
        if self.ui.logo_path and not Path(self.ui.logo_path).exists():
            # Warning only, not an error
            import warnings
            warnings.warn(f"Logo file not found: {self.ui.logo_path}")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
        _settings.validate()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = None
    return get_settings()