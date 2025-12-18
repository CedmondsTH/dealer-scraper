# 🚀 Dealer Scraper - Complete Handoff Guide

**Everything in One Place: For Management, Developers, and Troubleshooting**

---

## 📧 Executive Summary (For Management)

### What This Application Does

The **Dealer Scraper** is a web-based tool that automatically extracts dealership location data from dealer group websites and exports it to Excel format.

**Think of it as:** Google for dealer locations - instead of manually copying data from websites, this does it automatically in seconds.

### How to Access

**🌐 Live Application:** https://dealer-scraper-production.up.railway.app/

No installation needed - just open in any web browser and use it.

### What It Can Do

✅ **Extracts 100+ locations in under 30 seconds**  
✅ **Works with 8+ major dealer groups** (Lithia, Sonic, Group 1, Hudson, etc.)  
✅ **Handles most dealer websites** automatically via smart generic strategies  
✅ **Exports to Excel** with all contact information  
✅ **Hosted online 24/7** - accessible anywhere  

### Supported Dealer Groups (Tested & Working)

```
✅ Lithia Motors          (200+ locations)
✅ Sonic Automotive       (138+ locations)
✅ Group 1 Automotive     (154+ locations)
✅ Hudson Automotive      (Complex JavaScript sites)
✅ AutoCanada
✅ Cooper Auto Family
✅ Courtesy Automotive
✅ Ray Skillman
✅ Most other dealer groups (via generic strategies)
```

### Ongoing Costs

| Item | Cost | Notes |
|------|------|-------|
| **Railway Hosting** | $5-10/month | Keeps app running online 24/7 |
| **GitHub** | Free | Code repository |
| **Domain** | $0 | Uses Railway subdomain |
| **API Keys** | $0 | Optional AI features (not required) |

**Total Monthly Cost:** ~$5-10

### Technical Requirements

If you need to hire a developer to maintain/extend this:

**Required Skills:**
- Python 3.10+ experience
- Web scraping knowledge (BeautifulSoup, Playwright)
- Basic web development (Streamlit)
- Git/GitHub familiarity

**Nice to Have:**
- Docker/Railway deployment experience
- Testing frameworks (pytest)
- CI/CD pipeline knowledge

**Time to Onboard:**
- Experienced Python dev: 1-2 hours
- New to web scraping: 1 day
- Junior dev: 2-3 days

---

## 🌐 Where Everything Lives

### Live Application
**URL:** https://dealer-scraper-production.up.railway.app/  
**Status:** Active and deployed  
**Last Updated:** December 2025

### Code Repository
**GitHub:** https://github.com/CedmondsTH/dealer-scraper  
**Branch:** `main` (production)  
**Visibility:** Private (need access)

### Hosting Platform
**Platform:** Railway.app  
**Region:** US East  
**Auto-Deploy:** Yes (on push to main branch)  
**Account:** (credentials needed)

### Automatic Updates
Any code pushed to the `main` branch on GitHub automatically:
1. Runs quality checks (GitHub Actions)
2. Deploys to Railway (3-5 minutes)
3. Goes live at the production URL

---

## 📋 Complete Tech Stack

### Required Technologies

```
┌─────────────────────────────────────────────────────────────┐
│                  DEVELOPMENT ENVIRONMENT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🐍 Python 3.10 or 3.11     Programming language            │
│  📦 pip                     Package manager                  │
│  🌳 Git 2.x                 Version control                  │
│  💻 VS Code                 Code editor (recommended)        │
│  🔐 GitHub Account          Repository access                │
│  🚂 Railway Account         Hosting platform                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Core Python Packages

| Package | Version | Purpose | Required? |
|---------|---------|---------|-----------|
| streamlit | ≥1.28.0 | Web interface | ✅ YES |
| pandas | ≥1.5.0 | Data manipulation | ✅ YES |
| beautifulsoup4 | ≥4.11.0 | HTML parsing | ✅ YES |
| lxml | ≥4.9.0 | Fast HTML parser | ✅ YES |
| playwright | ≥1.30.0 | Browser automation | ✅ YES |
| requests | ≥2.28.0 | HTTP requests | ✅ YES |
| openpyxl | ≥3.0.0 | Excel files | ✅ YES |
| python-dotenv | ≥1.0.0 | Environment vars | ✅ YES |
| google-generativeai | ≥0.3.0 | AI fallback | ⚠️ Optional |
| openai | ≥1.0.0 | AI fallback | ⚠️ Optional |

### Development Tools (Optional)

- **pytest** - Automated testing
- **black** - Code formatting
- **flake8** - Code quality checks
- **mypy** - Type checking
- **isort** - Import organization

---

## 🏗️ System Architecture

### High-Level Overview

```
┌──────────────────────────────────────────────────────────────┐
│                                                               │
│                     👤 USER (Web Browser)                     │
│                             ↓                                 │
│        ┌────────────────────────────────────────┐            │
│        │   STREAMLIT WEB INTERFACE               │            │
│        │   • User enters dealer info             │            │
│        │   • Displays results                    │            │
│        │   • Downloads Excel                     │            │
│        └──────────────┬─────────────────────────┘            │
│                       ↓                                       │
│        ┌────────────────────────────────────────┐            │
│        │   SCRAPER SERVICE (Coordinator)         │            │
│        │   • Manages workflow                    │            │
│        │   • Handles retries                     │            │
│        │   • Coordinates components              │            │
│        └──────────────┬─────────────────────────┘            │
│                       ↓                                       │
│           ┌───────────┴──────────┐                           │
│           ↓                      ↓                            │
│  ┌────────────────┐    ┌────────────────┐                   │
│  │  WEB SCRAPER   │    │  DATA SERVICE  │                   │
│  │  Fetches HTML  │    │  Processes &   │                   │
│  │  from websites │    │  Exports data  │                   │
│  └────────┬───────┘    └────────┬───────┘                   │
│           ↓                     ↓                             │
│  ┌─────────────────────────────────────┐                    │
│  │    14 SCRAPING STRATEGIES            │                    │
│  │  ┌────────┬────────┬────────┐       │                    │
│  │  │ Lithia │ Sonic  │ Group1 │ +11   │                    │
│  │  └────────┴────────┴────────┘       │                    │
│  │  • 10 Dealer-Specific Strategies     │                    │
│  │  • 4 Generic Strategies              │                    │
│  └──────────────┬──────────────────────┘                    │
│                 ↓                                             │
│  ┌─────────────────────────────────┐                        │
│  │        UTILITIES                 │                        │
│  │  • Address Parser                │                        │
│  │  • Data Cleaner                  │                        │
│  │  • Deduplication                 │                        │
│  └──────────────┬──────────────────┘                        │
│                 ↓                                             │
│      ┌──────────────────────┐                               │
│      │   📊 EXCEL OUTPUT    │                               │
│      │   User downloads     │                               │
│      └──────────────────────┘                               │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow (6 Steps)

```
STEP 1: USER INPUT
┌─────────────────────┐
│ User enters:        │
│ • Dealer name       │
│ • Website URL       │
└──────────┬──────────┘
           ↓
STEP 2: FETCH WEBPAGE
┌─────────────────────┐
│ Download HTML:      │
│ • Try requests      │
│ • Use Playwright    │
│   for JS sites      │
└──────────┬──────────┘
           ↓
STEP 3: SELECT STRATEGY
┌─────────────────────┐
│ Choose extractor:   │
│ • Lithia strategy?  │
│ • Sonic strategy?   │
│ • Generic strategy? │
└──────────┬──────────┘
           ↓
STEP 4: EXTRACT DATA
┌─────────────────────┐
│ Parse HTML for:     │
│ • Names             │
│ • Addresses         │
│ • Phone numbers     │
│ • Websites          │
└──────────┬──────────┘
           ↓
STEP 5: CLEAN & VALIDATE
┌─────────────────────┐
│ Process data:       │
│ • Fix addresses     │
│ • Remove dupes      │
│ • Validate quality  │
└──────────┬──────────┘
           ↓
STEP 6: EXPORT TO EXCEL
┌─────────────────────┐
│ Create spreadsheet  │
│ User downloads ✓    │
└─────────────────────┘
```

---

## 📁 Project Structure

### Complete Folder Layout

```
dealer-scraper/
│
├── 📄 run.py                        ← Main entry point (starts app)
├── ⚙️  config.py                     ← All settings & configuration
├── 📋 requirements.txt              ← Python packages needed
├── 📋 requirements-dev.txt          ← Development tools
├── 🐳 Dockerfile                    ← Railway deployment config
├── 🚂 railway.json                  ← Railway settings
├── ▶️  start.sh                      ← Startup script
├── 📊 rules.json                    ← Learned scraping patterns
├── 📄 README.md                     ← Project overview
│
├── 📁 src/                          ← MAIN APPLICATION CODE
│   ├── 📄 models.py                 ← Data structures
│   ├── 📄 exceptions.py             ← Error handling
│   │
│   ├── 📁 scrapers/                 ← SCRAPING ENGINE
│   │   ├── 📄 base_scraper.py      ← Core logic
│   │   ├── 📄 scraper_registry.py  ← Strategy registration
│   │   ├── 📄 strategy_manager.py  ← Coordinates strategies
│   │   │
│   │   ├── 📁 strategies/           ← 14 EXTRACTION METHODS
│   │   │   ├── 📄 lithia_strategy.py
│   │   │   ├── 📄 sonic_dealercom_strategy.py
│   │   │   ├── 📄 group1_automotive_strategy.py
│   │   │   ├── 📄 hudson_automotive_strategy.py
│   │   │   ├── 📄 autocanada_strategy.py
│   │   │   ├── 📄 cooper_auto_strategy.py
│   │   │   ├── 📄 courtesy_automotive_strategy.py
│   │   │   ├── 📄 ray_skillman_strategy.py
│   │   │   ├── 📄 dealercom_content_blocks_strategy.py
│   │   │   ├── 📄 learned_rule_strategy.py
│   │   │   ├── 📄 overfuel_locations_strategy.py
│   │   │   ├── 📄 json_ld_strategy.py
│   │   │   ├── 📄 javascript_strategy.py
│   │   │   └── 📄 generic_dealer_strategy.py
│   │   │
│   │   └── 📁 extractors/           ← Reusable tools
│   │       ├── 📄 banister_extractor.py
│   │       ├── 📄 dealeron_extractor.py
│   │       └── 📄 heading_address_extractor.py
│   │
│   ├── 📁 services/                 ← BUSINESS LOGIC
│   │   ├── 📄 scraper_service.py   ← Main coordinator
│   │   ├── 📄 data_service.py      ← Data processing & Excel
│   │   ├── 📄 web_scraper.py       ← Fetches web pages
│   │   ├── 📄 playwright_subprocess.py ← JavaScript sites
│   │   └── 📄 rule_store.py        ← Pattern learning
│   │
│   ├── 📁 utils/                    ← HELPER TOOLS
│   │   ├── 📄 address_parser.py    ← Cleans addresses
│   │   └── 📄 data_cleaner.py      ← Removes duplicates
│   │
│   └── 📁 ui/                       ← USER INTERFACE
│       └── 📄 streamlit_app.py     ← Web app UI
│
├── 📁 tests/                        ← AUTOMATED TESTING
│   ├── 📄 test_basic.py
│   ├── 📄 test_integration_scraping.py
│   ├── 📁 unit/                     ← Component tests
│   └── 📁 integration/              ← Full system tests
│
├── 📁 docs/                         ← DOCUMENTATION
│   ├── 📄 HOW_IT_WORKS.md
│   ├── 📄 HANDOFF_NOTES.md
│   └── 📄 PROJECT_STRUCTURE.md
│
├── 📁 .github/workflows/            ← CI/CD AUTOMATION
│   ├── 📄 ci.yml                   ← Runs tests
│   └── 📄 integration-tests.yml    ← Daily tests
│
├── 📁 assets/                       ← IMAGES
│   └── 📄 trackhawk_logo.png
│
└── 📁 archive/                      ← OLD CODE (reference only)
```

### Key Files Explained

| File | Purpose | When to Edit |
|------|---------|--------------|
| `run.py` | Starts the application | Rarely - it's the entry point |
| `config.py` | All settings (timeouts, API keys, columns) | Change timeouts, add settings |
| `src/ui/streamlit_app.py` | Web interface code | Change UI text, layout, buttons |
| `src/services/scraper_service.py` | Orchestrates scraping workflow | Modify scraping logic |
| `src/scrapers/strategies/*.py` | Dealer-specific extraction logic | Add new dealer support |
| `src/utils/address_parser.py` | Address cleaning & parsing | Fix address format issues |
| `src/utils/data_cleaner.py` | Deduplication logic | Adjust duplicate detection |
| `requirements.txt` | Python packages | Add new dependencies |
| `Dockerfile` | Deployment configuration | Change deployment settings |
| `start.sh` | Startup script for Railway | Modify startup behavior |

---

## 🚀 Setup From Scratch (For Developers)

### Prerequisites Checklist

```
Before starting, you need:

☐ Computer (Windows, Mac, or Linux)
☐ Admin/sudo access
☐ Stable internet
☐ 2-3 GB free disk space
☐ 30-60 minutes of time
```

---

### Step 1️⃣: Install Python

**Download:** Go to [python.org/downloads](https://www.python.org/downloads/)

**Choose:** Python 3.11 (recommended) or Python 3.10

**⚠️ CRITICAL:** During installation, check **"Add Python to PATH"**

```
┌─────────────────────────────────────┐
│  Python 3.11.x Setup                │
├─────────────────────────────────────┤
│                                     │
│  ✅ Add Python 3.11 to PATH        │  ← CHECK THIS!
│  ☐ Install for all users           │
│                                     │
│      [Install Now]                  │
└─────────────────────────────────────┘
```

**Verify:**
```bash
python --version
# Should show: Python 3.11.x

pip --version
# Should show: pip 23.x.x
```

---

### Step 2️⃣: Install Git

**Download:** [git-scm.com](https://git-scm.com/)

**Install:** Use default settings

**Verify:**
```bash
git --version
# Should show: git version 2.x.x
```

**Optional Configuration:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

### Step 3️⃣: Clone Repository

```bash
# Navigate to desired location
cd C:\Projects  # Windows
# OR: cd ~/Projects  # Mac/Linux

# Clone the repository
git clone https://github.com/CedmondsTH/dealer-scraper.git

# Enter directory
cd dealer-scraper

# Verify you're on main branch
git branch
# Should show: * main
```

---

### Step 4️⃣: Create Virtual Environment

**Why?** Isolates dependencies from other projects

```bash
# Create virtual environment
python -m venv venv

# Activate it:

# WINDOWS:
venv\Scripts\activate

# MAC/LINUX:
source venv/bin/activate
```

**Success indicator:**
```bash
(venv) C:\Projects\dealer-scraper>
       ↑
  This shows venv is active
```

---

### Step 5️⃣: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Optional: Install development tools
pip install -r requirements-dev.txt

# Install Playwright browsers
playwright install chromium
```

**Takes:** 2-5 minutes

**What installs:**
```
✓ pandas
✓ beautifulsoup4
✓ lxml
✓ requests
✓ streamlit
✓ playwright
✓ openpyxl
... and more
```

---

### Step 6️⃣: Configure Environment

**Create `.env` file:**
```bash
# Windows:
type nul > .env

# Mac/Linux:
touch .env
```

**Content (optional):**
```env
# Only needed for AI fallback features
GEMINI_API_KEY=your_key_if_you_have_one
OPENAI_API_KEY=your_key_if_you_have_one
```

**Note:** App works fine without these keys!

---

### Step 7️⃣: Run Application

```bash
streamlit run run.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

**Browser should open automatically!** 🎉

---

### Step 8️⃣: Test It Works

**In the web interface:**

1. **Dealer Name:** `Lithia Motors`
2. **Website URL:** `https://www.lithia.com/locations.htm`
3. Click **"Extract Dealerships"**

**✅ Success:**
```
Successfully extracted 200+ dealerships!
[Download Excel]
```

**✅ Setup Complete!**

---

## 🔧 Development Workflow

### Standard Development Process

```
┌─────────────────────────────────────────────────┐
│         DEVELOPMENT CYCLE                        │
└─────────────────────────────────────────────────┘

1️⃣  START → Checkout main branch
    $ git checkout main

2️⃣  UPDATE → Pull latest changes
    $ git pull origin main

3️⃣  CODE → Make your changes
    (Edit files in VS Code)

4️⃣  TEST → Run locally
    $ streamlit run run.py
    Test thoroughly!

5️⃣  FORMAT → Clean up code
    $ black src/ tests/
    $ isort src/ tests/

6️⃣  STAGE → Add changes
    $ git add .

7️⃣  COMMIT → Save changes
    $ git commit -m "Description"

8️⃣  PUSH → Send to GitHub
    $ git push origin main

9️⃣  DEPLOY → Railway auto-deploys!
    ⏱️ 3-5 minutes
    🌐 Live at production URL

🔟 VERIFY → Test live site
    Check everything works!
```

### Deployment Flow Diagram

```
Developer Computer          GitHub              Railway
       │                      │                    │
       │  1. git push         │                    │
       │─────────────────────→│                    │
       │                      │                    │
       │                      │  2. Run Tests      │
       │                      │     ✓ Unit tests   │
       │                      │     ✓ Linting      │
       │                      │     ✓ Format       │
       │                      │                    │
       │                      │  3. Tests Pass     │
       │                      │────────────────────→│
       │                      │                    │
       │                      │          4. Build & Deploy
       │                      │          (3-5 minutes)
       │                      │                    │
       │                      │          5. App Live!
       │                      │          ✓ Health checks
       │                      │          ✓ Running
```

---

## 🐛 Top 5 Issues & How to Fix Them

### Issue #1: ModuleNotFoundError

```
┌──────────────────────────────────────────────────┐
│ ❌ ERROR                                          │
├──────────────────────────────────────────────────┤
│ ModuleNotFoundError: No module named 'streamlit' │
└──────────────────────────────────────────────────┘
```

**Cause:**
- Dependencies not installed
- Virtual environment not activated
- Wrong Python version

**Fix:**
```bash
# 1. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Verify
pip list | grep streamlit
```

---

### Issue #2: Playwright Browser Not Found

```
┌──────────────────────────────────────────────────┐
│ ❌ ERROR                                          │
├──────────────────────────────────────────────────┤
│ Error: Chromium browser not found                │
└──────────────────────────────────────────────────┘
```

**Cause:**
- Playwright browsers not installed

**Fix:**
```bash
# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium

# Linux only: Install dependencies
playwright install-deps chromium
```

---

### Issue #3: App Won't Start

```
┌──────────────────────────────────────────────────┐
│ ❌ ERROR                                          │
├──────────────────────────────────────────────────┤
│ Error: File does not exist: run.py               │
└──────────────────────────────────────────────────┘
```

**Cause:**
- Wrong directory

**Fix:**
```bash
# Check where you are
pwd  # Mac/Linux
cd   # Windows

# Navigate to project root
cd dealer-scraper

# Verify files exist
ls run.py src/ tests/  # Mac/Linux
dir run.py             # Windows

# Run app
streamlit run run.py
```

---

### Issue #4: Port Already in Use

```
┌──────────────────────────────────────────────────┐
│ ❌ ERROR                                          │
├──────────────────────────────────────────────────┤
│ Port 8501 is already in use                      │
└──────────────────────────────────────────────────┘
```

**Cause:**
- Another Streamlit instance running

**Fix Option A - Use Different Port:**
```bash
streamlit run run.py --server.port 8502
```

**Fix Option B - Kill Process:**
```bash
# Windows:
taskkill /F /IM streamlit.exe

# Mac/Linux:
pkill -f streamlit
```

---

### Issue #5: Railway Deployment Fails

```
┌──────────────────────────────────────────────────┐
│ ❌ RAILWAY ERROR                                  │
├──────────────────────────────────────────────────┤
│ Deployment failed                                 │
│ Health check failed                               │
└──────────────────────────────────────────────────┘
```

**Common Causes:**

**A. Missing Package**
```bash
# Add to requirements.txt
echo "package-name==1.2.3" >> requirements.txt
git add requirements.txt
git commit -m "Add missing package"
git push origin main
```

**B. Environment Variables**
1. Go to Railway dashboard
2. Click "Variables"
3. Add missing variables
4. Redeploy

**C. Check Logs**
1. Railway dashboard → Deployments
2. Click failed deployment
3. View "Deploy Logs" and "Runtime Logs"
4. Look for error messages

---

## 🎯 Common Development Tasks

### Task 1: Add New Dealer Group Support

**Example: Adding "Penske Automotive"**

**Step 1 - Create strategy file:**
```bash
touch src/scrapers/strategies/penske_strategy.py
```

**Step 2 - Write the strategy:**
```python
# src/scrapers/strategies/penske_strategy.py

from typing import List, Dict, Any
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import ScraperStrategy

class PenskeStrategy(ScraperStrategy):
    """Strategy for Penske Automotive"""
    
    def __init__(self):
        super().__init__()
        self.is_specific = True
    
    def strategy_name(self) -> str:
        return "Penske Automotive HTML"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        return "penskeautomotive.com" in page_url
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        dealers = []
        
        # Find dealer containers
        # (Inspect website to find correct selectors)
        for div in soup.find_all('div', class_='dealer-card'):
            name = div.find('h2').get_text(strip=True)
            address = div.find('div', class_='address').get_text(strip=True)
            
            dealers.append({
                'name': name,
                'street': address,
                # ... more fields
            })
        
        return dealers
```

**Step 3 - Register strategy:**
```python
# src/scrapers/strategy_manager.py

from src.scrapers.strategies.penske_strategy import PenskeStrategy

def initialize_strategies() -> None:
    # ... existing strategies ...
    scraper_registry.register(PenskeStrategy())  # Add this
```

**Step 4 - Test:**
```bash
streamlit run run.py
# Test with Penske website
```

---

### Task 2: Change Timeout Settings

```python
# Edit: config.py

class WebScraperConfig:
    timeout: int = 60  # Changed from 30 to 60 seconds
```

---

### Task 3: Modify UI Text

```python
# Edit: src/ui/streamlit_app.py

st.title("Your Custom Title")  # Change this

if st.button("Your Button Text"):  # Change this
    ...
```

---

### Task 4: Add Output Column

```python
# Edit: config.py

class Constants:
    OUTPUT_COLUMNS: List[str] = [
        "Dealership",
        "Your New Column",  # Add here
        "Address",
        ...
    ]
```

Then update scrapers to return this field.

---

## 🔍 Debugging & Troubleshooting

### Debug Locally

```bash
# Run with verbose logging
streamlit run run.py --logger.level=debug
```

### Check Railway Logs

```
Step 1: Go to https://railway.app

Step 2: Click your project

Step 3: Click "Deployments"

Step 4: Click the deployment you want to check

Step 5: View logs:
  ├─ Build Logs → Installation process
  ├─ Deploy Logs → Startup process
  └─ Runtime Logs → Running errors
```

### Test Components Individually

```python
# Create: test_component.py

from src.services.scraper_service import ScraperService

service = ScraperService()
result = service.scrape_dealer_locations(
    'Test Dealer',
    'https://example.com/locations'
)

print(f"Status: {result.status}")
print(f"Dealers: {len(result.dealers)}")
```

Run:
```bash
python test_component.py
```

### Useful Debug Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# Git status
git status

# Recent commits
git log --oneline -10

# Check which Python
which python  # Mac/Linux
where python  # Windows

# Kill Streamlit processes
pkill -f streamlit  # Mac/Linux
taskkill /F /IM streamlit.exe  # Windows
```

---

## 📞 Maintenance & Support

### If the App Goes Down

**Step 1: Check Railway**
- Go to Railway dashboard
- Check deployment status
- Look for error messages in logs

**Step 2: Try Redeploying**
- Click "Deploy" button in Railway
- Wait 3-5 minutes
- Check if app comes back online

**Step 3: Check GitHub Actions**
- Go to repository → Actions tab
- See if tests are failing
- Review error messages

### If a Specific Dealer Stops Working

**This is normal** - websites change their structure

**What to do:**
1. The app will still work for other dealers
2. A developer needs to update/create a strategy for that dealer
3. Takes 1-3 hours for an experienced developer

### For Code Changes

```bash
# Pull latest code
git pull origin main

# Make changes
# ... edit files ...

# Test locally
streamlit run run.py

# Push changes
git add .
git commit -m "Description"
git push origin main

# Railway auto-deploys in 3-5 minutes
```

---

## 📊 Project Metrics & Status

### Current Status

| Metric | Value |
|--------|-------|
| **Lines of Code** | ~3,500 |
| **Test Coverage** | Unit + Integration tests |
| **Supported Dealers** | 8+ specific, most generic |
| **Average Extraction Time** | 15-45 seconds |
| **Deployment Time** | 3-5 minutes (automatic) |
| **Uptime** | 99%+ |
| **Documentation** | Comprehensive |

### What's Included

```
✅ Web-based user interface
✅ 14 scraping strategies
✅ Address parsing & cleaning
✅ Duplicate removal
✅ Excel export
✅ Error handling & logging
✅ Automated testing
✅ CI/CD pipeline
✅ Comprehensive documentation
✅ Production deployment
```

---

## 🎓 For the Next Developer

### Onboarding Timeline

| Experience Level | Time to Productive |
|------------------|-------------------|
| **Experienced Python Developer** | 1-2 hours |
| **New to Web Scraping** | 1 day |
| **Junior Developer** | 2-3 days |

### Required Skills

**Must Have:**
- Python 3.10+ experience
- HTML/CSS basics
- Git/GitHub knowledge
- Command line comfort

**Should Have:**
- Web scraping experience (BeautifulSoup)
- HTTP/REST concepts
- Basic testing knowledge

**Nice to Have:**
- Playwright/Selenium
- Streamlit framework
- Docker/Railway
- CI/CD pipelines

### Learning Path

```
Day 1: Setup & Exploration
├─ Follow setup guide (30-60 min)
├─ Run app locally (10 min)
├─ Test with different dealers (30 min)
└─ Read HOW_IT_WORKS.md (1 hour)

Day 2: Code Understanding
├─ Explore project structure (1 hour)
├─ Read key files (2 hours)
├─ Understand data flow (1 hour)
└─ Review scraping strategies (2 hours)

Day 3: Make First Change
├─ Pick a small task (30 min)
├─ Make the change (1 hour)
├─ Test thoroughly (30 min)
├─ Deploy to Railway (30 min)
└─ Verify it works (30 min)

Week 2+: Full Productivity
├─ Add new dealer support
├─ Fix bugs
├─ Optimize performance
└─ Add features
```

---

## 📚 Documentation Reference

### All Available Documentation

```
Root Documentation:
├── COMPLETE_HANDOFF_GUIDE.md    ← THIS FILE (everything!)
├── README.md                     ← Project overview
├── HANDOFF_EMAIL_TEMPLATE.md    ← Email template
├── PROJECT_STRUCTURE_VISUAL.md  ← Visual guide
└── SIMPLIFIED_DIAGRAM.md        ← Flow charts

docs/ Folder:
├── HOW_IT_WORKS.md              ← Architecture deep dive
├── HANDOFF_NOTES.md             ← Maintenance guide
└── PROJECT_STRUCTURE.md         ← Detailed structure

GitHub:
└── .github/workflows/README.md  ← CI/CD documentation
```

### External Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| Python Docs | python.org/docs | Language reference |
| Streamlit Docs | docs.streamlit.io | Web framework |
| BeautifulSoup | crummy.com/software/BeautifulSoup | HTML parsing |
| Playwright | playwright.dev/python | Browser automation |
| Railway Docs | docs.railway.app | Hosting |
| Git Docs | git-scm.com/doc | Version control |

---

## ✅ Setup Checklist

Print and check off as you complete:

```
SETUP CHECKLIST:

☐ Install Python 3.10 or 3.11
☐ Install Git
☐ Clone repository
☐ Create virtual environment
☐ Activate virtual environment
☐ Install dependencies (requirements.txt)
☐ Install Playwright browsers
☐ Create .env file
☐ Run app locally
☐ Test with Lithia Motors
☐ Download Excel file successfully

OPTIONAL:
☐ Install dev tools (requirements-dev.txt)
☐ Set up VS Code
☐ Configure Git
☐ Get Railway access
☐ Get GitHub access

SUCCESS CRITERIA:
☐ App runs without errors
☐ Can extract dealerships
☐ Can download Excel
☐ Understand project structure
```

---

## 🎯 Quick Command Reference

### Git Commands

```bash
# Clone
git clone https://github.com/CedmondsTH/dealer-scraper.git

# Status
git status

# Pull changes
git pull origin main

# Stage all changes
git add .

# Commit
git commit -m "Description"

# Push
git push origin main

# View history
git log --oneline -10
```

### Python Commands

```bash
# Create virtual env
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Run app
streamlit run run.py
```

### Debugging Commands

```bash
# Check versions
python --version
git --version
pip --version

# List packages
pip list

# Kill Streamlit
pkill -f streamlit  # Mac/Linux
taskkill /F /IM streamlit.exe  # Windows
```

---

## 💼 Handoff Checklist for Management

Use this to ensure smooth transition:

```
TECHNICAL HANDOFF:

☐ Railway account access provided
☐ GitHub repository access granted
☐ Environment variables documented
☐ API keys transferred (if any)
☐ Domain/DNS settings documented
☐ Backup strategy explained

DOCUMENTATION:

☐ This guide shared with team
☐ Email template used for handoff
☐ All docs available on GitHub
☐ Video walkthrough recorded (optional)

KNOWLEDGE TRANSFER:

☐ Live demo conducted
☐ Q&A session completed
☐ Key contacts identified
☐ Escalation path defined

BUSINESS CONTINUITY:

☐ Monthly costs documented
☐ Vendor accounts listed
☐ Deployment process tested
☐ Rollback procedure documented
☐ Support contacts provided
```

---

## 🚀 Ready to Go!

**This guide contains everything needed to:**

✅ Understand what the app does  
✅ Know where everything is hosted  
✅ Set up the development environment  
✅ Make code changes  
✅ Deploy to production  
✅ Debug issues  
✅ Add new features  
✅ Maintain the application  

**For questions or issues:**
1. Check this guide first
2. Review error logs
3. Check GitHub Issues
4. Consult external documentation

---

**Project:** Dealer Scraper  
**Repository:** https://github.com/CedmondsTH/dealer-scraper  
**Live Application:** https://dealer-scraper-production.up.railway.app/  
**Last Updated:** December 2025  
**Status:** ✅ Production-Ready

---

*End of Complete Handoff Guide*

