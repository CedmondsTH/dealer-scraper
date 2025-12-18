# Migration Guide - Dealer Scraper v2.0

## Overview

This guide helps you migrate from the old codebase structure to the refactored v2.0 architecture.

**Target Audience:** Developers maintaining or extending the Dealer Scraper  
**Estimated Migration Time:** 15-30 minutes for basic usage updates

---

## What Changed?

### 1. Configuration System
**Old:** Multiple configuration files with inconsistent access patterns  
**New:** Single `config.py` with structured dataclass-based configuration

### 2. Entry Point
**Old:** Multiple entry points (`main.py`, `app.py`, `app_legacy.py`)  
**New:** Single `run.py` for both CLI and web modes

### 3. Import Structure
**Old:** Mixed imports from root-level modules and `src/`  
**New:** Consistent `src.` prefix for all application code

### 4. Exception Handling
**Old:** Generic `Exception` catching  
**New:** Domain-specific exceptions in `src/exceptions.py`

### 5. Logging
**Old:** Mix of `print()` statements and `self.logger`  
**New:** Module-level `logger` with proper log levels

---

## Quick Migration Checklist

- [ ] Update environment variables (see `.env` section)
- [ ] Update import statements (see Import Changes)
- [ ] Update entry point commands (see Running the Application)
- [ ] Test with your typical use cases
- [ ] Update any deployment scripts

---

## Detailed Changes

### Environment Variables

**Create a `.env` file** (copy from `env.example`):

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional (with defaults)
DEBUG=false
ENVIRONMENT=production

# Scraping Configuration
SCRAPING_TIMEOUT=60000
SCRAPING_HEADLESS=true
SCRAPING_VIEWPORT_WIDTH=1920
SCRAPING_VIEWPORT_HEIGHT=1080

# Data Processing
DATA_MAX_DEALERS=1000

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/app.log

# UI Configuration
UI_PAGE_TITLE=Dealer Group Dealership Scraper
UI_CACHE_ENABLED=true
```

### Import Changes

#### Configuration Imports

**Before:**
```python
from config.settings import config, Constants
```

**After:**
```python
from config import config, Constants
```

**Access Pattern Changes:**
```python
# Before
timeout = config.SCRAPING_TIMEOUT
brands = config.CAR_BRANDS

# After
timeout = config.scraping.timeout
brands = Constants.CAR_BRANDS
```

#### Module Imports

**Before:**
```python
from scrapers import scraper_manager
from utils.browser import browser_manager
from models.dealership import Dealership
```

**After:**
```python
from src.scrapers.strategy_manager import get_configured_scraper
from src.services.web_scraper import WebScraper
from src.models import Dealer
```

#### Service Imports

**Before:**
```python
from core.scraper_service import ScraperService
from core.data_service import DataService
```

**After:**
```python
from src.services.scraper_service import ScraperService
from src.services.data_service import DataService
```

### Running the Application

#### Web Interface

**Before:**
```bash
python app.py
# or
streamlit run app.py
# or
python main.py
```

**After:**
```bash
python run.py
# or
streamlit run run.py
```

#### CLI Mode

**Before:**
```bash
python main.py "Dealer Name" "https://dealer-url.com"
```

**After:**
```bash
python run.py "Dealer Name" "https://dealer-url.com"
```

#### Help

```bash
python run.py --help
```

### Exception Handling

**Before:**
```python
try:
    result = scraper.scrape(url)
except Exception as e:
    print(f"Error: {e}")
```

**After:**
```python
from src.exceptions import ScrapingError, PageFetchError

try:
    result = scraper.scrape(url)
except PageFetchError as e:
    logger.error(f"Failed to fetch page: {e}")
except ScrapingError as e:
    logger.error(f"Scraping failed: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
```

### Logging

**Before:**
```python
class MyClass:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def my_method(self):
        self.logger.info("Message")
        print("DEBUG: Something")  # ❌ Don't do this
```

**After:**
```python
import logging

logger = logging.getLogger(__name__)

class MyClass:
    def my_method(self):
        logger.info("Message")
        logger.debug("Something")  # ✅ Use proper log levels
```

### Creating New Strategies

**Before:**
```python
from ..base_scraper import ScraperStrategy

class MyStrategy(ScraperStrategy):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
```

**After:**
```python
import logging
from src.scrapers.base_scraper import ScraperStrategy

logger = logging.getLogger(__name__)

class MyStrategy(ScraperStrategy):
    # No __init__ needed unless you have other setup
    pass
```

---

## API Changes

### ScraperService

**Before:**
```python
service = ScraperService()
result = service.scrape_dealer_locations(dealer_name, url)
# result is a list
```

**After:**
```python
service = ScraperService()
result = service.scrape_dealer_locations(dealer_name, url)
# result is a ScrapingResult object
if result.success:
    dealers = result.dealers
else:
    print(result.message, result.error)
```

### DataService

**Before:**
```python
data_service = DataService()
df = data_service.create_dataframe(dealers)
excel_buffer = data_service.export_to_excel(dealers)
```

**After:**
```python
# Same API, but now raises specific exceptions
from src.exceptions import ExportError

data_service = DataService()
try:
    df = data_service.create_dataframe(dealers)
    excel_buffer = data_service.export_to_excel(dealers)
except ExportError as e:
    logger.error(f"Export failed: {e}")
```

### WebScraper

**Before:**
```python
scraper = WebScraper(ScrapingConfig())
html = scraper.fetch_page(url, save_debug=True)
```

**After:**
```python
# Configuration is automatic from config.py
scraper = WebScraper()
html = scraper.fetch_page(url, save_debug=True)
# Or let it use config default:
html = scraper.fetch_page(url)
```

---

## Deployment Changes

### Railway

**No changes required** to `railway.json`. The application automatically detects the environment.

**Environment Variables to Set:**
1. `GEMINI_API_KEY` (required)
2. `ENVIRONMENT=production`
3. `LOG_LEVEL=INFO`
4. Any other custom settings

**Build Command:** (unchanged)
```bash
pip install -r requirements.txt && playwright install chromium
```

**Start Command:**
```bash
streamlit run run.py --server.port=$PORT --server.address=0.0.0.0
```

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CedmondsTH/dealer-scraper.git
   cd dealer-scraper
   git checkout refactor/production-ready
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the application:**
   ```bash
   python run.py  # Web UI
   # or
   python run.py "Dealer Name" "URL"  # CLI
   ```

---

## Testing Your Migration

### 1. Configuration Test
```bash
python -c "from config import config; config.validate(); print('Config OK')"
```

### 2. Import Test
```python
from config import config, Constants
from src.services.scraper_service import ScraperService
from src.services.data_service import DataService
from src.services.web_scraper import WebScraper
print("All imports successful!")
```

### 3. Functional Test
```bash
# Test with a known working dealer site
python run.py "Lithia Motors" "https://www.lithia.com/locations"
```

### 4. Web UI Test
```bash
python run.py
# Open browser to http://localhost:8501
# Try scraping a dealer site
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'config.settings'"

**Problem:** Old import statement  
**Solution:** Update to `from config import config`

### "AttributeError: 'AppConfig' object has no attribute 'SCRAPING_TIMEOUT'"

**Problem:** Old configuration access pattern  
**Solution:** Use `config.scraping.timeout` instead of `config.SCRAPING_TIMEOUT`

### "ValueError: GEMINI_API_KEY environment variable is required"

**Problem:** Missing API key  
**Solution:** Add `GEMINI_API_KEY` to your `.env` file or environment variables

### "ImportError: cannot import name 'scraper_manager'"

**Problem:** Old import from root-level `scrapers/`  
**Solution:** Use `from src.scrapers.strategy_manager import get_configured_scraper`

### Logging not working

**Problem:** Using `self.logger` in new code  
**Solution:** Use module-level `logger = logging.getLogger(__name__)`

---

## Backwards Compatibility

### Deprecated (Still Works, But Will Be Removed)

- ❌ `main.py` - Use `run.py` instead
- ❌ `app.py` - Use `run.py` instead
- ❌ Root-level `scrapers/`, `models/`, `utils/` folders - Use `src/` versions
- ❌ `config/settings.py` - Use root `config.py`

### Removed

- ❌ `app_legacy.py` - Completely removed
- ❌ Old configuration system - Replaced entirely

---

## Getting Help

### Documentation
- `README.md` - General usage
- `HOW_IT_WORKS.md` - Architecture explanation
- `REFACTORING_PLAN.md` - Detailed refactoring plan
- This file - Migration guide

### Issues
- Check existing GitHub issues
- Create new issue with:
  - Error message
  - Steps to reproduce
  - Environment details (OS, Python version)

### Code Examples

See `tests/` directory for examples of:
- Using the new configuration
- Proper exception handling
- Testing strategies

---

## Summary of Benefits

After migration, you get:

✅ **Single source of truth** for configuration  
✅ **Better error messages** with specific exceptions  
✅ **Consistent imports** across the codebase  
✅ **Professional logging** with proper levels  
✅ **Easier testing** with better structure  
✅ **Clearer entry points** for CLI and web modes  
✅ **Better maintainability** for future changes  

---

**Questions?** Open an issue on GitHub or check the documentation files.

**Last Updated:** December 18, 2024  
**Version:** 2.0.0

