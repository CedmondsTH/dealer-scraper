# Dealer Scraper - Project Structure

This document provides an overview of the project structure and organization.

## Directory Structure

```
dealer-scraper/
│
├── .github/                    # CI/CD and GitHub configuration
│   └── workflows/             
│       ├── ci.yml             # Main CI pipeline
│       ├── integration-tests.yml
│       └── README.md          # Workflows documentation
│
├── archive/                    # Archived legacy files
│   ├── old_entry_points/      # Old app.py, main.py
│   ├── config_old/            # Legacy configuration
│   ├── models_old/            # Legacy models
│   ├── utils_old/             # Legacy utilities
│   ├── scrapers_old/          # Legacy scrapers
│   ├── ui_old/                # Outdated UI files
│   └── README.md              # Archive documentation
│
├── assets/                     # Static assets
│   └── trackhawk_logo.png     # Application logo
│
├── src/                        # Main source code
│   ├── scrapers/              # Scraping engine
│   │   ├── extractors/        # Modular data extractors
│   │   │   ├── banister_extractor.py
│   │   │   ├── dealeron_extractor.py
│   │   │   └── heading_address_extractor.py
│   │   ├── strategies/        # Scraping strategies
│   │   │   ├── lithia_strategy.py
│   │   │   ├── hudson_automotive_strategy.py
│   │   │   ├── generic_dealer_strategy.py
│   │   │   └── ... (14 total strategies)
│   │   ├── base_scraper.py    # Base scraper class
│   │   └── strategy_manager.py # Strategy registration
│   │
│   ├── services/              # Business logic
│   │   ├── scraper_service.py # Main scraping service
│   │   ├── data_service.py    # Data processing
│   │   ├── web_scraper.py     # Web fetching
│   │   └── playwright_subprocess.py
│   │
│   ├── utils/                 # Utility functions
│   │   ├── address_parser.py  # Address parsing
│   │   └── data_cleaner.py    # Data cleaning
│   │
│   ├── ui/                    # User interface
│   │   └── streamlit_app.py   # Streamlit web interface
│   │
│   ├── exceptions.py          # Custom exceptions
│   ├── models.py              # Data models
│   └── py.typed               # Type checking marker
│
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   │   ├── test_address_parser.py
│   │   ├── test_data_cleaner.py
│   │   └── test_scraper_service.py
│   ├── integration/           # Integration tests
│   │   └── test_end_to_end.py
│   ├── test_extractors.py     # Extractor tests
│   ├── test_integration_scraping.py
│   └── README.md              # Test documentation
│
├── config.py                   # Application configuration (MAIN)
├── run.py                      # Entry point (MAIN)
│
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
│
├── pytest.ini                  # Test configuration
├── mypy.ini                    # Type checking configuration
│
├── Dockerfile                  # Docker configuration
├── railway.json                # Railway deployment config
│
├── README.md                   # Main documentation (CONSOLIDATED)
├── FINAL_SUMMARY.md            # Project completion summary
├── HANDOFF_NOTES.md            # Quick reference guide
├── MIGRATION_GUIDE.md          # Migration instructions
├── REFACTORING_SUMMARY.md      # Technical improvements (CONSOLIDATED)
├── HOW_IT_WORKS.md             # Architecture explanation
│
├── LICENSE                     # License file
└── .gitignore                  # Git ignore rules
```

## Key Files

### Entry Points
- **`run.py`** - Unified entry point for both CLI and UI modes

### Configuration
- **`config.py`** - Single source of truth for all application settings

### Source Code
- **`src/scrapers/`** - All scraping logic and strategies
- **`src/services/`** - Business logic and orchestration
- **`src/utils/`** - Reusable utility functions
- **`src/ui/`** - Streamlit web interface

### Tests
- **`tests/unit/`** - Fast unit tests
- **`tests/integration/`** - End-to-end integration tests

### Documentation
- **`README.md`** - Primary user-facing documentation
- **`FINAL_SUMMARY.md`** - Complete project overview
- **`HANDOFF_NOTES.md`** - Quick start for new developers

## Clean Structure Features

✅ **No Duplicates**: All duplicate files archived  
✅ **Single UI Location**: `src/ui/` only  
✅ **Single Config**: `config.py` at root  
✅ **Consolidated Docs**: One README, one refactoring summary  
✅ **Clear Separation**: Source, tests, docs, and archive clearly separated  
✅ **Professional Layout**: Industry-standard Python project structure

## Import Paths

All imports use the standard Python package structure:

```python
# Services
from src.services.scraper_service import ScraperService

# Utilities
from src.utils.address_parser import parse_address

# Configuration
from config import config

# Models
from src.models import ScrapingResult
```

## Archive Folder

The `archive/` folder contains:
- Legacy entry points (old app.py, main.py)
- Old folder structures (config_old/, models_old/, utils_old/)
- Deprecated UI files
- Old documentation versions

These are kept for reference but are not used by the application.

---

*Last Updated: December 18, 2025*  
*Branch: refactor/production-ready*

