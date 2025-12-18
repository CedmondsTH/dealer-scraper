# Dealer Location Scraper v2.0

> **Professional-grade automotive dealership data extraction platform**

A robust, production-ready web application for extracting dealer location data from automotive dealer websites. Built with enterprise architecture, comprehensive error handling, and extensive dealer site support.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### Core Capabilities
- 🤖 **AI-Powered Extraction** - Gemini AI fallback for unlimited website support
- 🎯 **15+ Pre-Built Strategies** - Handles major dealer groups automatically
- 🔄 **Smart Retry Logic** - Automatic fallback with Playwright for JS-heavy sites
- 📍 **Sitemap Crawling** - Discovers individual location pages automatically
- 🌐 **Multi-Format Support** - JSON-LD, JavaScript variables, custom HTML patterns

### Data Quality
- ✅ **Address Validation** - Intelligent parsing and normalization
- 🔍 **Duplicate Detection** - Advanced deduplication algorithms
- 🏷️ **Brand Classification** - Automatic detection of 50+ automotive brands
- 📊 **Multiple Export Formats** - Excel, CSV, and JSON

### User Experience
- 💻 **Professional Web Interface** - Modern Streamlit UI with real-time progress
- ⚡ **CLI Mode** - Scriptable command-line interface for automation
- 📈 **Live Metrics** - Real-time extraction statistics
- 🎨 **Responsive Design** - Works on desktop and mobile

---

## 🏗️ Architecture

```
dealer-scraper/
├── config.py              # Centralized configuration
├── run.py                 # Main entry point (CLI + Web)
├── requirements.txt       # Dependencies
├── env.example           # Environment template
│
├── src/                  # Application code
│   ├── exceptions.py     # Custom exception hierarchy
│   ├── models.py         # Pydantic data models
│   │
│   ├── scrapers/         # Scraping strategies
│   │   ├── base_scraper.py
│   │   ├── scraper_registry.py
│   │   ├── strategy_manager.py
│   │   └── strategies/   # 15+ dealer-specific strategies
│   │
│   ├── services/         # Business logic
│   │   ├── scraper_service.py    # Main orchestrator
│   │   ├── data_service.py       # Data processing
│   │   ├── web_scraper.py        # Page fetching
│   │   └── playwright_subprocess.py
│   │
│   ├── utils/           # Utilities
│   │   ├── address_parser.py
│   │   ├── data_cleaner.py
│   │   └── ...
│   │
│   └── ui/              # Web interface
│       └── streamlit_app.py
│
├── tests/               # Test suite
│   ├── test_basic.py
│   └── ...
│
└── docs/               # Documentation
    ├── HOW_IT_WORKS.md
    ├── MIGRATION_GUIDE.md
    └── REFACTORING_PLAN.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- 2GB RAM minimum
- Internet connection

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CedmondsTH/dealer-scraper.git
   cd dealer-scraper
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
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
   # Web Interface
   python run.py
   
   # CLI Mode
   python run.py "Lithia Motors" "https://www.lithia.com/locations"
   ```

---

## 💻 Usage

### Web Interface

Start the web interface:
```bash
python run.py
```

Then open your browser to `http://localhost:8501`

**Steps:**
1. Enter the dealer group name (e.g., "Lithia Motors")
2. Paste the locations page URL
3. Click "Extract Dealerships"
4. Download results in Excel, CSV, or JSON format

### Command Line Interface

Extract dealer data programmatically:

```bash
# Basic usage
python run.py "Dealer Name" "https://dealer-website.com/locations"

# Output is JSON (can be piped to other tools)
python run.py "Lithia Motors" "https://lithia.com/locations" > dealers.json

# Get help
python run.py --help
```

### Python API

Use as a library in your Python code:

```python
from config import config
from src.services.scraper_service import ScraperService

# Configure
config.validate()

# Initialize service
scraper = ScraperService()

# Scrape
result = scraper.scrape_dealer_locations(
    dealer_name="Lithia Motors",
    url="https://www.lithia.com/locations"
)

if result.success:
    print(f"Extracted {len(result.dealers)} dealers")
    for dealer in result.dealers:
        print(f"- {dealer['Dealership']}: {dealer['Address']}")
else:
    print(f"Failed: {result.message}")
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (see `env.example`):

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (with defaults shown)
DEBUG=false
ENVIRONMENT=production

# Scraping
SCRAPING_TIMEOUT=60000
SCRAPING_HEADLESS=true
SCRAPING_VIEWPORT_WIDTH=1920
SCRAPING_VIEWPORT_HEIGHT=1080
SCRAPING_MAX_RETRIES=3

# Data Processing
DATA_MAX_DEALERS=1000
DATA_VALIDATE_ADDRESSES=true

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/app.log

# UI
UI_PAGE_TITLE=Dealer Group Dealership Scraper
UI_CACHE_ENABLED=true
```

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

---

## 🎯 Supported Dealer Sites

### Major Dealer Groups
- ✅ **Lithia Motors** - Complete network coverage
- ✅ **Group 1 Automotive** - Multi-brand locations
- ✅ **AutoCanada** - Canadian dealer network
- ✅ **Sonic Automotive** - DealerCom sites
- ✅ **Cooper Automotive** - Custom site format
- ✅ **Courtesy Automotive** - Regional dealer group
- ✅ **Ray Skillman** - Indianapolis area dealers

### Generic Support
- ✅ **JSON-LD Sites** - Standards-compliant structured data
- ✅ **JavaScript Variables** - Sites using `var locations = [...]`
- ✅ **DealerCom Platforms** - Multiple DealerCom formats
- ✅ **Custom HTML** - 10+ generic HTML patterns
- ✅ **AI Fallback** - Any site via Gemini AI

### Total Coverage
- **15+ pre-built strategies**
- **Unlimited sites** via AI fallback
- **Automatic strategy selection**
- **Sitemap discovery** for multi-page sites

---

## 📊 Data Output

### Output Columns

| Column | Description | Example |
|--------|-------------|---------|
| Dealership | Dealer name | "Lithia Toyota of Springfield" |
| Dealer Group | Parent company | "Lithia Motors" |
| Dealership Type | Category | "Franchised", "Used", "Collision", "Fixed Ops" |
| Car Brand | Detected brands | "Toyota; Lexus" |
| Address | Street address | "123 Main St" |
| City | City name | "Springfield" |
| State/Province | State/province code | "OR" |
| Postal Code | ZIP/postal code | "97477" |
| Phone | Contact number | "(541) 555-1234" |
| Country | Country name | "United States of America" |
| Website | Dealer website | "lithiatoyota.com" |

### Data Quality Features

- **Address Normalization** - Standardizes abbreviations (Street→St, Avenue→Ave)
- **Duplicate Removal** - Based on normalized name and address
- **Phone Validation** - Extracts and formats phone numbers
- **Brand Detection** - Identifies 50+ automotive brands
- **Country Classification** - US/Canada based on state/province
- **Type Classification** - Franchised, Used, Collision, Fixed Ops

---

## 🧪 Development

### Adding New Dealer Sites

1. **Create a new strategy** in `src/scrapers/strategies/`:

```python
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from src.scrapers.base_scraper import ScraperStrategy

logger = logging.getLogger(__name__)


class MyDealerStrategy(ScraperStrategy):
    """Scraper for MyDealer website format."""
    
    @property
    def strategy_name(self) -> str:
        return "MyDealer Format"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if this strategy can handle the page."""
        return "mydealer.com" in page_url or "my-dealer-indicator" in html
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealer data from the page."""
        soup = BeautifulSoup(html, "html.parser")
        dealers = []
        
        # Your extraction logic here
        for location in soup.find_all('div', class_='location'):
            dealer = {
                'name': location.find('h3').get_text(strip=True),
                'street': location.find('span', class_='address').get_text(strip=True),
                'city': location.find('span', class_='city').get_text(strip=True),
                'state': location.find('span', class_='state').get_text(strip=True),
                'zip': location.find('span', class_='zip').get_text(strip=True),
                'phone': location.find('a', class_='phone').get_text(strip=True),
                'website': page_url
            }
            dealers.append(dealer)
        
        logger.info(f"Extracted {len(dealers)} dealers using MyDealer strategy")
        return dealers
```

2. **Register the strategy** in `src/scrapers/strategy_manager.py`:

```python
from src.scrapers.strategies.my_dealer_strategy import MyDealerStrategy

def initialize_strategies() -> None:
    # ... existing strategies ...
    scraper_registry.register(MyDealerStrategy())
    # ... rest of strategies ...
```

3. **Test your strategy:**

```bash
python run.py "MyDealer Group" "https://mydealer.com/locations"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_basic.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

---

## 🚢 Deployment

### Railway

1. **Fork the repository** on GitHub

2. **Create new Railway project:**
   - Visit [Railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository

3. **Configure environment variables:**
   ```
   GEMINI_API_KEY=your_key_here
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```

4. **Deploy:**
   - Railway automatically detects `railway.json`
   - Build and start commands are pre-configured
   - Application will be available at your Railway URL

### Docker (Optional)

```bash
# Build image
docker build -t dealer-scraper .

# Run container
docker run -p 8501:8501 \
  -e GEMINI_API_KEY=your_key_here \
  dealer-scraper
```

---

## 📚 Documentation

- **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** - Architecture deep dive
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Upgrading from v1.x
- **[REFACTORING_PLAN.md](REFACTORING_PLAN.md)** - Development roadmap
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution
- 🎯 New dealer site strategies
- 🧪 Test coverage improvements
- 📚 Documentation enhancements
- 🐛 Bug fixes
- ✨ Feature requests

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Common Issues

**"GEMINI_API_KEY environment variable is required"**
- Add your API key to `.env` file
- Get a free key at [Google AI Studio](https://makersuite.google.com/app/apikey)

**"No dealers found"**
- Website structure may have changed
- Try a different URL (main locations page)
- Check if AI fallback is enabled

**"Failed to fetch page content"**
- Website may be blocking automated requests
- Playwright fallback should handle this automatically
- Check your internet connection

### Getting Help

1. **Check documentation** - Most questions are answered in the docs
2. **Search issues** - Someone may have had the same problem
3. **Create an issue** - Include error messages and steps to reproduce
4. **Provide details** - OS, Python version, full error traceback

---

## 🏆 Professional Standards

This codebase follows enterprise development best practices:

- ✅ **Clean Architecture** - Separation of concerns
- ✅ **SOLID Principles** - Maintainable design
- ✅ **Strategy Pattern** - Extensible scraping
- ✅ **Service Layer** - Testable business logic
- ✅ **Type Safety** - Comprehensive type hints
- ✅ **Error Handling** - Domain-specific exceptions
- ✅ **Professional Logging** - Structured output
- ✅ **Configuration Management** - Environment-based settings

---

## 📈 Performance

- **Fast scraping** - Requests-first approach (90% of sites)
- **Parallel processing** - Multiple URLs scraped concurrently
- **Smart caching** - Avoids re-scraping in web interface
- **Memory efficient** - Automatic browser cleanup
- **Scalable** - Handles 1000+ dealers per run

---

## 🔒 Security & Privacy

- **No data storage** - Scraped data is not stored on servers
- **Browser isolation** - Each session uses fresh browser instance
- **Rate limiting** - Respectful scraping with delays
- **Error handling** - No sensitive information in logs
- **API key security** - Environment variable based configuration

---

**Built with ❤️ for the automotive industry**

**Version:** 2.0.0  
**Last Updated:** December 18, 2024  
**Maintainer:** [CedmondsTH](https://github.com/CedmondsTH)

---

## Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!


