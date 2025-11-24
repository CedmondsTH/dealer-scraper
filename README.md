# Dealer Location Scraper

A professional-grade web application for extracting dealer location data from automotive dealer websites. Built with a modular architecture supporting multiple dealer site formats and providing clean, validated output.

## 🚀 Features

- **Multi-Strategy Scraping**: Automatically detects and handles 6+ different dealer website formats
- **Clean Data Output**: Validates addresses, removes duplicates, normalizes data
- **Multiple Export Formats**: Excel, CSV, and JSON output options
- **Professional Web Interface**: User-friendly Streamlit interface
- **Enterprise Architecture**: Modular, testable, and maintainable codebase

## 🏗️ Architecture

```
dealer-scraper/
├── core/           # Business logic services
├── scrapers/       # Modular scraping strategies  
├── ui/            # Web interface
├── cli/           # Command-line interface
├── utils/         # Shared utilities
├── config/        # Configuration management
└── archive/       # Historical files
```

## 🔧 Supported Dealer Sites

- **Lithia Motors** - Complete dealer network
- **Group 1 Automotive** - Multi-brand locations
- **AutoCanada** - Canadian dealer network
- **JSON-LD Sites** - Standards-compliant structured data
- **JavaScript-Based Sites** - Dynamic content extraction
- **Generic Sites** - HGreg, Ken Ganley, Sierra Auto, and 9+ other formats

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dealer-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Run the web interface**
   ```bash
   python main.py
   ```

4. **Or use the command line**
   ```bash
   python main.py scrape "Dealer Name" "https://dealer-website.com/locations"
   ```

### Railway Deployment

The application is configured for one-click Railway deployment:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

## 💻 Usage

### Web Interface

1. Visit the deployed application
2. Enter the dealer group name (e.g., "Lithia Motors")
3. Paste the dealer locations page URL
4. Click "Extract Dealerships"
5. Download the Excel or CSV file

### Command Line Interface

```bash
# Extract dealer data
python main.py scrape "Lithia Motors" "https://lithia.com/locations"

# List available scraping strategies
python main.py list-strategies

# Get help
python main.py --help
```

### Legacy Compatibility

```bash
# Old format still supported
python app.py "Dealer Name" "https://dealer-url.com"
```

## 🔧 Configuration

Configure the application via environment variables:

```bash
# Scraping settings
SCRAPING_TIMEOUT=60000
SCRAPING_HEADLESS=true
SCRAPING_VIEWPORT_WIDTH=1920

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/app.log

# UI settings
UI_PAGE_TITLE="Dealer Location Scraper"
UI_CACHE_ENABLED=true
```

## 🏛️ Professional Architecture

### Core Services

- **ScraperService**: Main orchestrator coordinating all operations
- **DataService**: Data processing, validation, and export functionality
- **WebScraper**: Browser automation with Playwright

### Strategy Pattern

Each dealer site type has its own specialized parser:

```python
from scrapers.strategies.lithia_strategy import LithiaStrategy
from scrapers.strategies.json_ld_strategy import JsonLdStrategy

# Strategies are automatically registered and used
```

### Utilities

- **AddressParser**: Converts full addresses into components
- **DataCleaner**: Validates, normalizes, and deduplicates data

## 🧪 Development

### Adding New Dealer Sites

1. Create a new strategy in `scrapers/strategies/`
2. Inherit from `ScraperStrategy` base class
3. Implement `can_handle()` and `extract_dealers()` methods
4. Register in `strategy_manager.py`

Example:

```python
class NewDealerStrategy(ScraperStrategy):
    @property
    def strategy_name(self) -> str:
        return "New Dealer Site"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        # Detection logic
        return "new-dealer-indicator" in html
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict]:
        # Extraction logic
        pass
```

### Testing

```bash
# Test specific dealer site
python main.py scrape "Test Dealer" "https://example.com" --debug

# List available strategies
python main.py list-strategies
```

## 📊 Data Output

### Excel/CSV Columns

- **Dealership**: Dealer name
- **Dealer Group**: Parent company
- **Dealership Type**: Franchised, Used, Collision, Fixed Ops
- **Car Brand**: Detected automotive brands
- **Address**: Street address (normalized)
- **City**: City name
- **State/Province**: State or province code
- **Postal Code**: ZIP or postal code
- **Phone**: Contact phone number
- **Country**: United States of America or Canada
- **Website**: Dealer website URL

### Data Quality

- **Address Normalization**: Standardizes abbreviations (Street→St, Avenue→Ave)
- **Duplicate Removal**: Based on normalized name and address
- **Phone Validation**: Extracts and formats phone numbers
- **Brand Detection**: Identifies automotive brands from dealer names

## 🔒 Security & Privacy

- **No data storage**: Scraped data is not stored on servers
- **Browser isolation**: Each scraping session uses fresh browser instance
- **Rate limiting**: Respectful scraping with appropriate delays
- **Error handling**: Graceful failure without exposing sensitive information

## 📈 Performance

- **Parallel processing**: Multiple extraction strategies run concurrently
- **Caching**: Web interface caches results to avoid re-scraping
- **Browser optimization**: Headless mode with performance optimizations
- **Memory management**: Automatic cleanup of browser resources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check existing GitHub issues
- Create a new issue with reproduction steps
- Include debug logs when reporting problems

## 🏆 Professional Standards

This codebase follows enterprise development standards:
- **Clean Architecture** with separation of concerns
- **SOLID Principles** throughout the design
- **Strategy Pattern** for extensible scraping
- **Service Layer** for testable business logic
- **Configuration Management** for environment-specific settings
- **Professional Logging** with structured output
- **Type Safety** with comprehensive type hints