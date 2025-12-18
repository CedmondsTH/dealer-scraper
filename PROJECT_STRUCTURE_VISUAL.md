# Dealer Scraper - Project Structure Guide

## 📊 Visual Folder Layout

```
dealer-scraper/
│
├── 📁 src/                              ← Main application code
│   ├── 📁 scrapers/                     ← Website scraping logic
│   │   ├── 📁 strategies/               ← Different methods to extract data
│   │   │   ├── lithia_strategy.py       (Lithia Motors specific)
│   │   │   ├── sonic_dealercom_strategy.py (Sonic Automotive specific)
│   │   │   ├── group1_automotive_strategy.py
│   │   │   ├── hudson_automotive_strategy.py
│   │   │   └── generic_dealer_strategy.py (Works with most websites)
│   │   │
│   │   ├── 📁 extractors/               ← Reusable data extraction tools
│   │   │   ├── banister_extractor.py
│   │   │   ├── dealeron_extractor.py
│   │   │   └── heading_address_extractor.py
│   │   │
│   │   └── base_scraper.py              ← Core scraping engine
│   │
│   ├── 📁 services/                     ← Business logic & coordination
│   │   ├── scraper_service.py           ← Main scraping coordinator
│   │   ├── data_service.py              ← Data processing & export
│   │   ├── web_scraper.py               ← Fetches web pages
│   │   └── playwright_subprocess.py     ← JavaScript-heavy websites
│   │
│   ├── 📁 utils/                        ← Helper tools
│   │   ├── address_parser.py            ← Cleans up addresses
│   │   └── data_cleaner.py              ← Removes duplicates
│   │
│   ├── 📁 ui/                           ← User interface
│   │   └── streamlit_app.py             ← Web app interface
│   │
│   ├── models.py                        ← Data structure definitions
│   ├── exceptions.py                    ← Error handling
│   └── config.py                        ← Settings & configuration
│
├── 📁 tests/                            ← Automated testing
│   ├── 📁 unit/                         ← Individual component tests
│   ├── 📁 integration/                  ← Full system tests
│   └── test_integration_scraping.py     ← Main test suite
│
├── 📁 docs/                             ← Documentation
│   ├── HOW_IT_WORKS.md                  ← Technical explanation
│   ├── HANDOFF_NOTES.md                 ← Maintenance guide
│   └── PROJECT_STRUCTURE.md             ← Detailed structure
│
├── 📁 .github/workflows/                ← Automated quality checks
│   ├── ci.yml                           ← Runs tests on code changes
│   └── integration-tests.yml            ← Daily automated testing
│
├── 📁 assets/                           ← Images & logos
│   └── trackhawk_logo.png
│
├── 📁 archive/                          ← Old code (kept for reference)
│
├── 🐳 Dockerfile                        ← Builds the app for Railway
├── 🚂 railway.json                      ← Railway deployment settings
├── ▶️ start.sh                          ← Startup script for Railway
├── ▶️ run.py                            ← Main app entry point
│
├── 📋 requirements.txt                  ← Python packages needed
├── 📋 requirements-dev.txt              ← Development tools
│
├── ⚙️ config.py                         ← Main configuration file
├── 📊 rules.json                        ← Learned scraping patterns
│
└── 📄 README.md                         ← Project overview
```

---

## 🎯 Key Files Explained (Non-Technical)

### **Essential Files to Know:**

| File | What It Does | Why It Matters |
|------|-------------|----------------|
| `run.py` | Starts the application | This is the "power button" |
| `config.py` | Stores all settings | Change settings here (timeouts, API keys, etc.) |
| `src/ui/streamlit_app.py` | The web interface users see | What your employees interact with |
| `src/services/scraper_service.py` | Coordinates all scraping | The "brain" of the operation |
| `requirements.txt` | List of software dependencies | Needed to install the app |
| `Dockerfile` | Instructions for Railway hosting | Keeps the app running online |
| `README.md` | Project overview & instructions | First place to look for help |

### **Folders Explained:**

| Folder | Purpose | Example |
|--------|---------|---------|
| `src/scrapers/strategies/` | Different methods to extract data from dealer websites | Each major dealer group (Lithia, Sonic, etc.) has a custom strategy |
| `src/services/` | Handles fetching pages, processing data, exporting to Excel | The "workers" that do the heavy lifting |
| `src/utils/` | Reusable tools (address parsing, deduplication) | Helper tools used throughout the app |
| `tests/` | Automated tests to catch bugs | Runs automatically on code changes |
| `docs/` | Documentation & guides | Instructions for future developers |
| `.github/workflows/` | Automated quality checks | Ensures code changes don't break things |
| `archive/` | Old code kept for reference | Safe to ignore, but don't delete |

---

## 🔄 How Data Flows Through the System

```
1. USER enters dealer name & website
   ↓
2. WEB SCRAPER fetches the webpage
   ↓
3. STRATEGIES try different extraction methods
   ↓
4. DATA CLEANER removes duplicates & fixes addresses
   ↓
5. DATA SERVICE formats into spreadsheet
   ↓
6. USER downloads Excel file
```

---

## 🚀 Deployment & Hosting

**Where the app lives:**
- **Production URL**: https://dealer-scraper-production.up.railway.app/
- **Hosting Platform**: Railway.app
- **Repository**: https://github.com/CedmondsTH/dealer-scraper

**How it updates:**
- Any code pushed to the `main` branch on GitHub automatically deploys to Railway
- Takes 3-5 minutes to rebuild and deploy
- GitHub Actions run automatic quality checks before deployment

---

## 📞 For Non-Technical Managers

### **What This App Does:**
Automatically extracts dealership location data (name, address, phone, website) from dealer group websites and exports it to Excel.

### **Supported Dealer Groups:**
✅ Lithia Motors  
✅ Sonic Automotive  
✅ Group 1 Automotive  
✅ Hudson Automotive  
✅ AutoCanada  
✅ Cooper Auto Family  
✅ Courtesy Automotive  
✅ Ray Skillman  
✅ **Most other dealer groups** (via generic strategies)

### **What You Need to Know:**
1. **App is hosted online** - accessible via web browser, no installation needed
2. **Automatic updates** - code changes deploy automatically
3. **Self-maintaining** - automated tests catch bugs before deployment
4. **Costs**: Railway hosting (~$5-10/month for basic usage)

### **If Something Breaks:**
1. Check the Railway dashboard for deployment errors
2. Review GitHub Actions for failed tests
3. Check `docs/HANDOFF_NOTES.md` for common issues
4. Contact a Python developer familiar with web scraping

---

## 📈 Recent Improvements

✅ Refactored for maintainability  
✅ Added comprehensive testing  
✅ Set up CI/CD pipeline  
✅ Deployed to Railway  
✅ Fixed duplicate data issues  
✅ Added support for JavaScript-heavy websites  
✅ Cleaned up project structure  
✅ Documented everything  

**Status**: Production-ready and professionally structured

