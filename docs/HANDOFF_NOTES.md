# Dealer Scraper - Handoff Notes

## For the Next Developer

Hi! If you're reading this, you're taking over maintenance of the Dealer Scraper application. This document will help you get up to speed quickly.

---

## What This Application Does

The Dealer Scraper extracts dealership location data from automotive dealer group websites. Users enter a dealer group name and URL, and get back an Excel file with hundreds of dealer locations including addresses, phone numbers, and other details.

**Key Features:**
- Supports 15+ dealer group website formats
- AI fallback for unlimited site support (via Gemini)
- Professional web interface (Streamlit)
- CLI mode for automation
- Exports to Excel, CSV, and JSON

---

## Recent Refactoring (December 2024)

The codebase was professionally refactored to make it more maintainable and less likely to break. Here's what changed:

### What Was Fixed
1. **Configuration** - Consolidated two config systems into one (`config.py`)
2. **Entry Point** - Single `run.py` instead of multiple entry points
3. **Error Handling** - Custom exceptions instead of generic errors
4. **Logging** - Professional logging instead of print statements
5. **Documentation** - Comprehensive docs for everything

### What You Need to Know
- **Main entry point:** `run.py` (not `main.py` or `app.py`)
- **Configuration:** `config.py` at root (not `config/settings.py`)
- **All code:** Lives in `src/` folder
- **Documentation:** `README_V2.md`, `MIGRATION_GUIDE.md`, `HOW_IT_WORKS.md`

---

## Quick Start

### Running the Application

```bash
# Web Interface
python run.py

# CLI Mode
python run.py "Dealer Name" "https://dealer-url.com/locations"

# Help
python run.py --help
```

### Configuration

1. Copy `env.example` to `.env`
2. Add your `GEMINI_API_KEY` (required)
3. Adjust other settings as needed

### Testing

```bash
# Test with a known working site
python run.py "Lithia Motors" "https://www.lithia.com/locations"
```

---

## Common Tasks

### Adding a New Dealer Site

1. **Create strategy file** in `src/scrapers/strategies/`:
   ```python
   # src/scrapers/strategies/my_dealer_strategy.py
   import logging
   from src.scrapers.base_scraper import ScraperStrategy
   
   logger = logging.getLogger(__name__)
   
   class MyDealerStrategy(ScraperStrategy):
       @property
       def strategy_name(self) -> str:
           return "MyDealer Format"
       
       def can_handle(self, html: str, page_url: str) -> bool:
           return "mydealer.com" in page_url
       
       def extract_dealers(self, html: str, page_url: str):
           # Your extraction logic here
           pass
   ```

2. **Register it** in `src/scrapers/strategy_manager.py`:
   ```python
   from src.scrapers.strategies.my_dealer_strategy import MyDealerStrategy
   
   def initialize_strategies():
       # ... existing strategies ...
       scraper_registry.register(MyDealerStrategy())
   ```

3. **Test it:**
   ```bash
   python run.py "MyDealer" "https://mydealer.com/locations"
   ```

### Debugging a Failing Site

1. **Enable debug mode:**
   ```bash
   # In .env
   DEBUG=true
   SCRAPING_DEBUG_FILES=true
   LOG_LEVEL=DEBUG
   ```

2. **Run the scraper:**
   ```bash
   python run.py "Dealer Name" "URL"
   ```

3. **Check debug files:**
   - Look for `debug_*.html` files in the current directory
   - Check logs for which strategy was used
   - Look for error messages in the output

4. **Common issues:**
   - Website structure changed → Update the strategy
   - Website blocking requests → Playwright fallback should handle it
   - No dealers found → Check if URL is correct, try AI fallback

### Updating Configuration

Edit `config.py` (not `.env` for code changes):

```python
# config.py

# Add new configuration
@dataclass
class ScrapingConfig:
    timeout: int = int(os.getenv('SCRAPING_TIMEOUT', '60000'))
    # Add your new setting here
    new_setting: str = os.getenv('NEW_SETTING', 'default_value')
```

Then use it:
```python
from config import config
value = config.scraping.new_setting
```

---

## Architecture Overview

```
dealer-scraper/
├── config.py              # Configuration (START HERE)
├── run.py                 # Entry point
├── src/
│   ├── exceptions.py      # Custom exceptions
│   ├── models.py          # Data models
│   ├── scrapers/          # Scraping strategies
│   ├── services/          # Business logic
│   ├── utils/             # Utilities
│   └── ui/                # Web interface
└── tests/                 # Tests
```

### Key Files

- **`config.py`** - All configuration
- **`run.py`** - Main entry point
- **`src/services/scraper_service.py`** - Main orchestrator
- **`src/services/web_scraper.py`** - Fetches web pages
- **`src/services/data_service.py`** - Processes data
- **`src/scrapers/strategy_manager.py`** - Registers strategies
- **`src/ui/streamlit_app.py`** - Web interface

---

## Common Problems & Solutions

### "GEMINI_API_KEY environment variable is required"
**Solution:** Add your API key to `.env` file

### "No dealers found"
**Solutions:**
- Check if URL is correct (should be locations page)
- Try enabling AI fallback
- Check debug HTML files to see what was fetched
- Website structure may have changed

### "Failed to fetch page content"
**Solutions:**
- Check internet connection
- Website may be blocking requests (Playwright should handle this)
- Try with `force_playwright=True`

### Import errors
**Solution:** Make sure you're using `src.` prefix:
```python
from src.services.scraper_service import ScraperService  # ✅
from services.scraper_service import ScraperService      # ❌
```

---

## Testing Strategy

### Manual Testing
1. Test with known working sites (Lithia, Group 1)
2. Test with new sites you're adding
3. Test both web UI and CLI modes
4. Test all export formats

### Automated Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_basic.py
```

---

## Deployment

### Railway (Current Deployment)
1. Push to GitHub
2. Railway auto-deploys from `main` branch
3. Set environment variables in Railway dashboard
4. Check logs if something breaks

### Local Development
1. Clone repo
2. Create virtual environment
3. Install dependencies
4. Create `.env` file
5. Run `python run.py`

---

## Code Style

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# Use proper log levels
logger.debug("Detailed info for debugging")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")

# Don't use print() except in CLI output
```

### Exceptions
```python
from src.exceptions import ScrapingError, PageFetchError

# Raise specific exceptions
raise PageFetchError(url, "Reason")

# Catch specific exceptions
try:
    result = scraper.scrape(url)
except PageFetchError as e:
    logger.error(f"Failed: {e}")
```

### Imports
```python
# Use src. prefix for application code
from src.services.scraper_service import ScraperService
from src.utils.data_cleaner import data_cleaner

# Use config for configuration
from config import config, Constants
```

---

## Documentation

- **`README_V2.md`** - Complete user documentation
- **`MIGRATION_GUIDE.md`** - Upgrading from old version
- **`HOW_IT_WORKS.md`** - Architecture deep dive
- **`REFACTORING_PLAN.md`** - Refactoring details
- **`REFACTORING_SUMMARY_V2.md`** - What was changed
- **This file** - Quick reference for developers

---

## Performance Tips

1. **Requests first** - 90% of sites work with simple requests
2. **Playwright fallback** - Only used when needed
3. **Parallel processing** - Multiple URLs scraped concurrently
4. **Caching** - Web UI caches results

---

## Security Notes

- **No data storage** - Scraped data is not stored on servers
- **API keys** - Always use environment variables, never hardcode
- **Rate limiting** - Be respectful to websites
- **Error messages** - Don't expose sensitive information

---

## Getting Help

1. **Check documentation** - Most answers are in the docs
2. **Check logs** - Enable DEBUG logging
3. **Check debug files** - HTML files show what was fetched
4. **Search issues** - Someone may have had the same problem
5. **Create issue** - Include error messages and steps to reproduce

---

## Maintenance Schedule

### Weekly
- Check Railway logs for errors
- Monitor Gemini API usage
- Test with major dealer sites

### Monthly
- Update dependencies
- Check for website changes
- Review error logs

### Quarterly
- Update documentation
- Review and optimize strategies
- Check for deprecated dependencies

---

## Known Issues

1. **Some sites block automated requests** - Playwright fallback handles most cases
2. **Website structures change** - Strategies need periodic updates
3. **AI fallback costs money** - Monitor Gemini API usage

---

## Future Improvements

### High Priority
- Expand test coverage
- Add CI/CD pipeline
- Performance monitoring

### Medium Priority
- Admin UI for learned rules
- Better error recovery
- More comprehensive logging

### Low Priority
- Database for rule storage
- API endpoint
- Scheduled scraping

---

## Contact

- **Repository:** https://github.com/CedmondsTH/dealer-scraper
- **Branch:** `refactor/production-ready`
- **Issues:** GitHub Issues
- **Documentation:** See docs/ folder

---

## Final Notes

This codebase has been professionally refactored to be:
- ✅ Easy to understand
- ✅ Well documented
- ✅ Following best practices
- ✅ Less likely to break
- ✅ Easy to maintain

**Don't be afraid to:**
- Add new strategies
- Modify existing code
- Ask questions (via GitHub issues)
- Improve the documentation

**Do be careful with:**
- Changing core architecture
- Modifying configuration structure
- Breaking backwards compatibility
- Removing error handling

---

**Good luck! The code is in good shape. You've got this! 🚀**

---

**Last Updated:** December 18, 2024  
**Version:** 2.0.0  
**Status:** Production Ready

