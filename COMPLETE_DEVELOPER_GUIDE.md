# 🚀 Dealer Scraper - Complete Developer Guide

**Everything you need to set up, edit, and troubleshoot the Dealer Scraper application**

---

## 📑 Table of Contents

1. [Tech Stack Overview](#-tech-stack-overview)
2. [System Architecture](#-system-architecture)
3. [Setup From Scratch](#-setup-from-scratch-step-by-step)
4. [Development Workflow](#-development-workflow)
5. [Top 5 Issues & Fixes](#-top-5-issues--fixes)
6. [Project Structure](#-project-structure)
7. [Common Tasks](#-common-development-tasks)
8. [Debugging Guide](#-debugging-guide)

---

## 📋 Tech Stack Overview

### Required Technologies & Tools

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT ENVIRONMENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🐍 Python 3.10 or 3.11      Core programming language          │
│  📦 pip                      Package manager (comes with Python) │
│  🌳 Git                      Version control                     │
│  💻 VS Code (recommended)    Code editor                         │
│  🔐 GitHub Account           Code repository access              │
│  🚂 Railway Account          Hosting/deployment platform         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Python Packages (Installed via requirements.txt)

| Package | Version | Purpose | Critical? |
|---------|---------|---------|-----------|
| **streamlit** | ≥1.28.0 | Web UI framework | ✅ YES |
| **pandas** | ≥1.5.0 | Data manipulation | ✅ YES |
| **beautifulsoup4** | ≥4.11.0 | HTML parsing | ✅ YES |
| **lxml** | ≥4.9.0 | Fast HTML parser | ✅ YES |
| **playwright** | ≥1.30.0 | Browser automation | ✅ YES |
| **requests** | ≥2.28.0 | HTTP requests | ✅ YES |
| **openpyxl** | ≥3.0.0 | Excel file creation | ✅ YES |
| **python-dotenv** | ≥1.0.0 | Environment variables | ✅ YES |
| **google-generativeai** | ≥0.3.0 | AI fallback (optional) | ⚠️ NO |
| **openai** | ≥1.0.0 | AI fallback (optional) | ⚠️ NO |

### Development Tools (Optional but Recommended)

| Tool | Purpose | Installation |
|------|---------|--------------|
| **pytest** | Testing framework | `pip install -r requirements-dev.txt` |
| **black** | Code formatter | Included in requirements-dev.txt |
| **flake8** | Linting | Included in requirements-dev.txt |
| **mypy** | Type checking | Included in requirements-dev.txt |
| **isort** | Import sorting | Included in requirements-dev.txt |

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                          👤 USER                                     │
│                    (Web Browser)                                     │
│                            │                                         │
│                            ↓                                         │
│        ┌───────────────────────────────────────┐                   │
│        │     STREAMLIT WEB INTERFACE            │                   │
│        │    (src/ui/streamlit_app.py)          │                   │
│        └──────────────┬────────────────────────┘                   │
│                       │                                              │
│                       ↓                                              │
│        ┌───────────────────────────────────────┐                   │
│        │      SCRAPER SERVICE                   │                   │
│        │  (src/services/scraper_service.py)    │                   │
│        │  • Coordinates scraping workflow       │                   │
│        │  • Handles retries & fallbacks         │                   │
│        └──────────────┬────────────────────────┘                   │
│                       │                                              │
│           ┌───────────┴───────────┐                                │
│           ↓                       ↓                                 │
│  ┌─────────────────┐     ┌─────────────────┐                      │
│  │  WEB SCRAPER    │     │  DATA SERVICE   │                      │
│  │  (Fetches HTML) │     │  (Processes &   │                      │
│  │                 │     │   Exports Data) │                      │
│  └────────┬────────┘     └────────┬────────┘                      │
│           │                       │                                 │
│           ↓                       ↓                                 │
│  ┌──────────────────────────────────────┐                         │
│  │     SCRAPING STRATEGIES               │                         │
│  │  ┌──────┐ ┌──────┐ ┌──────┐         │                         │
│  │  │Lithia│ │Sonic │ │Group1│ ... 14x │                         │
│  │  └──────┘ └──────┘ └──────┘         │                         │
│  └──────────────────┬───────────────────┘                         │
│                     │                                               │
│                     ↓                                               │
│  ┌──────────────────────────────────────┐                         │
│  │         UTILITIES                     │                         │
│  │  • Address Parser                     │                         │
│  │  • Data Cleaner                       │                         │
│  │  • Deduplication                      │                         │
│  └──────────────────────────────────────┘                         │
│                     │                                               │
│                     ↓                                               │
│        ┌───────────────────────────────┐                          │
│        │   📊 EXCEL EXPORT              │                          │
│        │   (Downloaded by user)         │                          │
│        └───────────────────────────────┘                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
┌─────────────┐
│   USER      │  1. Enters dealer name + URL
│   INPUT     │
└──────┬──────┘
       │
       ↓
┌─────────────────────┐
│  FETCH WEBPAGE      │  2. Download HTML
│  • Try requests     │     (or use Playwright for JS sites)
│  • Fallback to      │
│    Playwright       │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────────────────────────────────┐
│  SELECT STRATEGY                                 │
│  • Check if Lithia → Use Lithia strategy        │  3. Try different
│  • Check if Sonic → Use Sonic strategy          │     extraction
│  • Check if Group1 → Use Group1 strategy        │     methods
│  • Unknown? → Try generic strategies             │
└──────┬──────────────────────────────────────────┘
       │
       ↓
┌─────────────────────┐
│  EXTRACT DATA       │  4. Parse HTML to find:
│  • Dealership names │     - Names
│  • Addresses        │     - Addresses  
│  • Phone numbers    │     - Phones
│  • Websites         │     - Websites
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│  CLEAN & VALIDATE   │  5. Process data:
│  • Parse addresses  │     - Fix formats
│  • Remove dupes     │     - Remove duplicates
│  • Validate fields  │     - Validate quality
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│  FORMAT & EXPORT    │  6. Create Excel file
│  • Create DataFrame │
│  • Add columns      │
│  • Generate .xlsx   │
└──────┬──────────────┘
       │
       ↓
┌─────────────────────┐
│  USER DOWNLOADS     │  ✅ Complete!
│  EXCEL FILE         │
└─────────────────────┘
```

---

## 🚀 Setup From Scratch (Step-by-Step)

### Prerequisites Checklist

```
Before you begin, make sure you have:

☐ A computer with Windows, Mac, or Linux
☐ Administrative/sudo access (to install software)
☐ Stable internet connection
☐ 2-3 GB of free disk space
☐ 30-60 minutes of time
```

---

### Step 1️⃣: Install Python

**Download & Install:**

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python **3.11** (recommended) or **3.10**
3. Run the installer

**⚠️ CRITICAL:** Check **"Add Python to PATH"** during installation!

```
┌────────────────────────────────────────┐
│  Python 3.11.x Setup                   │
├────────────────────────────────────────┤
│                                        │
│  ✅ Add Python 3.11 to PATH           │  ← MUST CHECK THIS!
│  ☐ Install launcher for all users     │
│  ☐ Customize installation             │
│                                        │
│         [Install Now]                  │
│                                        │
└────────────────────────────────────────┘
```

**Verify Installation:**

```bash
python --version
# Expected output: Python 3.11.x

pip --version
# Expected output: pip 23.x.x from ...
```

---

### Step 2️⃣: Install Git

**Download & Install:**

1. Go to [git-scm.com](https://git-scm.com/)
2. Download for your OS
3. Install with default settings

**Verify Installation:**

```bash
git --version
# Expected output: git version 2.x.x
```

**Optional - Configure Git:**

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

### Step 3️⃣: Clone the Repository

```bash
# Navigate to where you want the project
cd C:\Projects  # Windows example
# OR: cd ~/Projects  # Mac/Linux example

# Clone the repository
git clone https://github.com/CedmondsTH/dealer-scraper.git

# Enter the project directory
cd dealer-scraper

# Verify you're on main branch
git branch
# Should show: * main
```

**What this does:**
```
Downloads:  ✅ All source code
           ✅ All documentation
           ✅ Configuration files
           ✅ Test files
```

---

### Step 4️⃣: Create Virtual Environment

**Why?** Isolates project dependencies from other Python projects.

```bash
# Create virtual environment
python -m venv venv

# Activate it:

# On WINDOWS:
venv\Scripts\activate

# On MAC/LINUX:
source venv/bin/activate
```

**You'll know it worked when you see:**
```bash
(venv) C:\Projects\dealer-scraper>
        ↑
    This prefix shows venv is active
```

---

### Step 5️⃣: Install Dependencies

```bash
# Install production packages (REQUIRED)
pip install -r requirements.txt

# Install development tools (OPTIONAL but recommended)
pip install -r requirements-dev.txt

# Install Playwright browsers (REQUIRED)
playwright install chromium
```

**Installation Progress:**
```
Installing collected packages...
✓ pandas
✓ beautifulsoup4
✓ lxml
✓ requests
✓ streamlit
✓ playwright
✓ openpyxl
... (and more)

Successfully installed 25 packages
```

**This takes:** 2-5 minutes depending on internet speed

---

### Step 6️⃣: Configure Environment Variables

**Create `.env` file:**

```bash
# Windows:
type nul > .env

# Mac/Linux:
touch .env
```

**Edit `.env` file** (optional - app works without these):

```env
# Optional: Only needed for AI fallback features
GEMINI_API_KEY=your_key_here_if_you_have_one
OPENAI_API_KEY=your_key_here_if_you_have_one
```

**Note:** The app works perfectly without these keys - they're only for experimental AI fallback.

---

### Step 7️⃣: Run the Application

```bash
streamlit run run.py
```

**Expected Output:**
```
Collecting usage statistics...

You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

**Your browser should automatically open!** 🎉

If not, manually open: `http://localhost:8501`

---

### Step 8️⃣: Test It Works

**In the web app:**

```
┌────────────────────────────────────────────────┐
│           Dealer Scraper                       │
├────────────────────────────────────────────────┤
│                                                │
│  Dealer Group Name:                            │
│  [Lithia Motors                          ]     │
│                                                │
│  Website URL:                                  │
│  [https://www.lithia.com/locations.htm   ]     │
│                                                │
│        [Extract Dealerships]                   │
│                                                │
└────────────────────────────────────────────────┘
```

**Click "Extract Dealerships"**

**✅ Success looks like:**
```
Successfully extracted 200+ dealerships!

[Download Excel]
```

---

### ✅ Setup Complete!

You should now have:
- ✅ Python installed
- ✅ Git installed
- ✅ Repository cloned
- ✅ Virtual environment active
- ✅ All dependencies installed
- ✅ App running locally
- ✅ Successful test scrape

**Time to complete:** 30-60 minutes

---

## 🔧 Development Workflow

### Making Changes - Standard Process

```
┌──────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT CYCLE                          │
└──────────────────────────────────────────────────────────────┘

1️⃣  START
    └─> Make sure you're on main branch
        $ git checkout main

2️⃣  UPDATE
    └─> Pull latest changes
        $ git pull origin main

3️⃣  EDIT
    └─> Make your code changes
        (Use VS Code or your favorite editor)

4️⃣  TEST LOCALLY
    └─> Run the app
        $ streamlit run run.py
        Test your changes thoroughly!

5️⃣  FORMAT CODE
    └─> Auto-format (if you have dev tools)
        $ black src/ tests/
        $ isort src/ tests/

6️⃣  COMMIT
    └─> Stage and commit
        $ git add .
        $ git commit -m "Description of your changes"

7️⃣  PUSH
    └─> Push to GitHub
        $ git push origin main

8️⃣  AUTO-DEPLOY
    └─> Railway automatically deploys!
        ⏱️ Takes 3-5 minutes
        🌐 Live at: dealer-scraper-production.up.railway.app

9️⃣  VERIFY
    └─> Test the live site
        Make sure everything works!
```

### Git Commands Quick Reference

```bash
# Check current status
git status

# See what changed
git diff

# View commit history
git log --oneline -10

# Undo uncommitted changes
git restore filename.py

# Create a new branch (optional)
git checkout -b feature/my-new-feature

# Switch branches
git checkout main

# See all branches
git branch -a
```

---

## 🐛 Top 5 Issues & Fixes

### Issue #1: ModuleNotFoundError

```
┌──────────────────────────────────────────────────────────┐
│ ❌ ERROR                                                  │
├──────────────────────────────────────────────────────────┤
│ ModuleNotFoundError: No module named 'streamlit'         │
│                                                           │
│ OR                                                        │
│                                                           │
│ ModuleNotFoundError: No module named 'pandas'            │
└──────────────────────────────────────────────────────────┘
```

**📋 Cause:**
- Dependencies not installed
- Wrong Python environment
- Virtual environment not activated

**✅ Fix:**

```bash
# 1. Make sure virtual environment is activated
#    You should see (venv) in your terminal

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Verify installation
pip list | grep streamlit
# Should show: streamlit  1.28.0 (or similar)

# 4. Try running again
streamlit run run.py
```

**🔍 How to Check What's Wrong:**

```bash
# Which Python is being used?
which python  # Mac/Linux
where python  # Windows

# What packages are installed?
pip list

# Is virtual environment active?
# Look for (venv) prefix in terminal
```

---

### Issue #2: Playwright/Browser Errors

```
┌──────────────────────────────────────────────────────────┐
│ ❌ ERROR                                                  │
├──────────────────────────────────────────────────────────┤
│ Error: Chromium browser not found                        │
│                                                           │
│ OR                                                        │
│                                                           │
│ playwright._impl._api_types.Error:                       │
│ Executable doesn't exist                                  │
└──────────────────────────────────────────────────────────┘
```

**📋 Cause:**
- Playwright browsers not installed
- System dependencies missing (Linux)

**✅ Fix:**

```bash
# 1. Install Playwright package (if not already)
pip install playwright

# 2. Install Chromium browser
playwright install chromium

# 3. (Linux only) Install system dependencies
playwright install-deps chromium

# 4. Verify installation
playwright --version
# Should show: Version 1.x.x
```

**📁 Where Playwright Installs Browsers:**

```
Windows: C:\Users\YourName\AppData\Local\ms-playwright\
Mac:     ~/Library/Caches/ms-playwright/
Linux:   ~/.cache/ms-playwright/
```

---

### Issue #3: App Won't Start

```
┌──────────────────────────────────────────────────────────┐
│ ❌ ERROR                                                  │
├──────────────────────────────────────────────────────────┤
│ Error: Invalid value: File does not exist: run.py        │
└──────────────────────────────────────────────────────────┘
```

**📋 Cause:**
- Not in the correct directory
- File was deleted or renamed

**✅ Fix:**

```bash
# 1. Check where you are
pwd  # Mac/Linux
cd   # Windows (shows current directory)

# 2. Navigate to project root
cd dealer-scraper

# 3. Verify files exist
ls  # Mac/Linux
dir # Windows

# You should see:
# run.py ✓
# src/ ✓
# tests/ ✓
# requirements.txt ✓

# 4. Now run the app
streamlit run run.py
```

**Visual Guide:**

```
✅ CORRECT:
C:\Projects\dealer-scraper> streamlit run run.py
                           ↑
            You're in the project root

❌ WRONG:
C:\Projects> streamlit run run.py
            ↑
  You're one level too high!
```

---

### Issue #4: Port Already in Use

```
┌──────────────────────────────────────────────────────────┐
│ ❌ ERROR                                                  │
├──────────────────────────────────────────────────────────┤
│ OSError: [Errno 48] Address already in use               │
│ Port 8501 is already in use                              │
└──────────────────────────────────────────────────────────┘
```

**📋 Cause:**
- Another Streamlit instance is running
- Another app is using port 8501

**✅ Fix - Option A: Use Different Port**

```bash
streamlit run run.py --server.port 8502

# Access at: http://localhost:8502
```

**✅ Fix - Option B: Kill Existing Process**

```bash
# Windows:
tasklist | findstr streamlit
# Note the PID, then:
taskkill /F /PID <PID_NUMBER>

# Mac/Linux:
ps aux | grep streamlit
# Note the PID, then:
kill -9 <PID_NUMBER>

# OR simpler:
pkill -f streamlit
```

---

### Issue #5: Railway Deployment Fails

```
┌──────────────────────────────────────────────────────────┐
│ ❌ RAILWAY ERROR                                          │
├──────────────────────────────────────────────────────────┤
│ Deployment failed                                         │
│ Build completed but service crashed                       │
│ Health check failed                                       │
└──────────────────────────────────────────────────────────┘
```

**📋 Common Causes & Fixes:**

#### **A. Missing Package**

```bash
# If you added a new package locally but forgot to add it to requirements.txt

# 1. Check what you have installed
pip freeze

# 2. Find the package you need
pip freeze | grep package-name

# 3. Add it to requirements.txt
echo "package-name==1.2.3" >> requirements.txt

# 4. Commit and push
git add requirements.txt
git commit -m "Add missing package"
git push origin main
```

#### **B. Environment Variables**

```
1. Go to Railway dashboard
2. Click your project
3. Click "Variables" tab
4. Add missing variables:
   - PORT (usually auto-set by Railway)
   - GEMINI_API_KEY (if using AI features)
   - OPENAI_API_KEY (if using AI features)
5. Click "Deploy"
```

#### **C. Port Configuration**

```bash
# Verify start.sh is executable
git update-index --chmod=+x start.sh
git add start.sh
git commit -m "Make start.sh executable"
git push origin main
```

#### **D. Check Railway Logs**

```
1. Go to: https://railway.app
2. Click your project
3. Click "Deployments"
4. Click the failed deployment
5. View "Deploy Logs"
   └─> Look for error messages
6. View "Runtime Logs" (if it started)
   └─> Check for Python errors
```

**Common Error Patterns:**

| Error in Logs | Meaning | Fix |
|---------------|---------|-----|
| `ModuleNotFoundError` | Missing package | Add to requirements.txt |
| `Port 8080 already in use` | Port config issue | Check start.sh |
| `No module named 'openai'` | Missing package | Add to requirements.txt |
| `Timeout during build` | Build too slow | Normal, just redeploy |
| `Health check failed` | App crashed on start | Check runtime logs |

---

## 📁 Project Structure

### Visual Folder Layout

```
dealer-scraper/
│
├── 📄 run.py                    ← START HERE! Main entry point
├── ⚙️  config.py                 ← Settings & configuration
├── 📋 requirements.txt          ← Production dependencies
├── 📋 requirements-dev.txt      ← Development dependencies
├── 🐳 Dockerfile                ← Railway deployment config
├── 🚂 railway.json              ← Railway settings
├── ▶️  start.sh                  ← Startup script (Railway)
├── 📊 rules.json                ← Learned scraping patterns
│
├── 📁 src/                      ← MAIN APPLICATION CODE
│   ├── 📄 __init__.py
│   ├── 📄 models.py             ← Data models
│   ├── 📄 exceptions.py         ← Custom errors
│   ├── 📄 config.py             ← Config classes
│   │
│   ├── 📁 scrapers/             ← SCRAPING LOGIC
│   │   ├── 📄 base_scraper.py  ← Core engine
│   │   ├── 📄 scraper_registry.py
│   │   ├── 📄 strategy_manager.py
│   │   │
│   │   ├── 📁 strategies/       ← 14 SCRAPING STRATEGIES
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
│   │   └── 📁 extractors/       ← REUSABLE EXTRACTORS
│   │       ├── 📄 banister_extractor.py
│   │       ├── 📄 dealeron_extractor.py
│   │       └── 📄 heading_address_extractor.py
│   │
│   ├── 📁 services/             ← BUSINESS LOGIC
│   │   ├── 📄 scraper_service.py      ← Main coordinator
│   │   ├── 📄 data_service.py         ← Data processing
│   │   ├── 📄 web_scraper.py          ← HTTP fetching
│   │   ├── 📄 playwright_subprocess.py ← Browser automation
│   │   └── 📄 rule_store.py           ← Pattern learning
│   │
│   ├── 📁 utils/                ← HELPER TOOLS
│   │   ├── 📄 address_parser.py ← Address cleaning
│   │   └── 📄 data_cleaner.py   ← Deduplication
│   │
│   └── 📁 ui/                   ← USER INTERFACE
│       └── 📄 streamlit_app.py  ← Web UI
│
├── 📁 tests/                    ← AUTOMATED TESTS
│   ├── 📄 conftest.py
│   ├── 📄 test_basic.py
│   ├── 📄 test_integration_scraping.py
│   ├── 📁 unit/
│   │   ├── 📄 test_address_parser.py
│   │   ├── 📄 test_data_cleaner.py
│   │   └── 📄 test_scraper_service.py
│   └── 📁 integration/
│       └── 📄 test_end_to_end.py
│
├── 📁 docs/                     ← DOCUMENTATION
│   ├── 📄 HOW_IT_WORKS.md
│   ├── 📄 HANDOFF_NOTES.md
│   └── 📄 PROJECT_STRUCTURE.md
│
├── 📁 .github/                  ← CI/CD
│   └── 📁 workflows/
│       ├── 📄 ci.yml            ← Automated tests
│       └── 📄 integration-tests.yml
│
├── 📁 assets/                   ← IMAGES
│   └── 📄 trackhawk_logo.png
│
└── 📁 archive/                  ← OLD CODE (safe to ignore)
    └── (legacy files...)
```

### Key Files Explained

| File | What It Does | When to Edit |
|------|-------------|--------------|
| `run.py` | Starts the Streamlit app | Rarely - entry point |
| `config.py` | All settings (timeouts, API keys) | Change timeouts, add settings |
| `src/ui/streamlit_app.py` | Web interface code | Change UI text, layout, buttons |
| `src/services/scraper_service.py` | Orchestrates scraping | Modify scraping workflow |
| `src/scrapers/strategies/*.py` | Dealer-specific extraction | Add new dealer support |
| `src/utils/address_parser.py` | Address parsing logic | Fix address formatting |
| `src/utils/data_cleaner.py` | Deduplication logic | Adjust duplicate detection |
| `requirements.txt` | Python packages needed | Add new dependencies |
| `Dockerfile` | Railway deployment | Change deployment config |
| `start.sh` | Startup script | Modify startup behavior |

---

## 🎯 Common Development Tasks

### Task 1: Add Support for a New Dealer Group

```
┌──────────────────────────────────────────────────────────┐
│  GOAL: Make the app work with "Penske Automotive"        │
└──────────────────────────────────────────────────────────┘

Step 1️⃣: Create new strategy file
$ touch src/scrapers/strategies/penske_strategy.py

Step 2️⃣: Copy template from existing strategy
# Open lithia_strategy.py or sonic_dealercom_strategy.py
# Copy the structure

Step 3️⃣: Implement the strategy
```

```python
# src/scrapers/strategies/penske_strategy.py

from typing import List, Dict, Any
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import ScraperStrategy

class PenskeStrategy(ScraperStrategy):
    """Strategy for Penske Automotive websites"""
    
    def __init__(self):
        super().__init__()
        self.is_specific = True  # Mark as dealer-specific
    
    def strategy_name(self) -> str:
        return "Penske Automotive HTML"
    
    def can_handle(self, html: str, page_url: str) -> bool:
        """Check if this is a Penske website"""
        return "penskeautomotive.com" in page_url
    
    def extract_dealers(self, html: str, page_url: str) -> List[Dict[str, Any]]:
        """Extract dealership data from Penske's website"""
        soup = BeautifulSoup(html, "lxml")
        dealers = []
        
        # Find dealership containers
        # (Inspect their website to find the right selectors)
        dealership_divs = soup.find_all('div', class_='dealership-card')
        
        for div in dealership_divs:
            name = div.find('h2', class_='dealer-name')
            address = div.find('div', class_='address')
            phone = div.find('a', class_='phone')
            
            if name and address:
                dealers.append({
                    'name': name.get_text(strip=True),
                    'street': address.get_text(strip=True),
                    'city': 'Parse from address',
                    'state': 'Parse from address',
                    'zip_code': 'Parse from address',
                    'phone': phone.get_text(strip=True) if phone else '',
                    'website': page_url,
                    'source_url': page_url
                })
        
        return dealers
```

```
Step 4️⃣: Register the strategy
```

```python
# src/scrapers/strategy_manager.py

from src.scrapers.strategies.penske_strategy import PenskeStrategy  # Add this

def initialize_strategies() -> None:
    # ... existing strategies ...
    scraper_registry.register(PenskeStrategy())  # Add this line
    # ... more strategies ...
```

```
Step 5️⃣: Test locally
$ streamlit run run.py

# In the app:
Dealer Name: Penske Automotive
URL: https://www.penskeautomotive.com/locations

# Click Extract and verify results
```

---

### Task 2: Change Timeout Settings

```python
# Edit: config.py

class WebScraperConfig:
    timeout: int = 30  # ← Change from 30 to 60 seconds
    
    # Increase for slow-loading websites
    # Decrease for faster scraping
```

---

### Task 3: Modify UI Text

```python
# Edit: src/ui/streamlit_app.py

# Change page title
st.set_page_config(
    page_title="Your Custom Title",  # ← Edit this
    ...
)

# Change header
st.title("Your Custom Header")  # ← Edit this

# Change button text
if st.button("Your Custom Button Text"):  # ← Edit this
    ...
```

---

### Task 4: Add a New Output Column

```python
# Edit: config.py

class Constants:
    OUTPUT_COLUMNS: List[str] = [
        "Dealership",
        "Dealer Group",
        "Your New Column",  # ← Add here
        "Address",
        "City",
        ...
    ]
```

Then make sure your scrapers return this field:

```python
# In your strategy:
dealers.append({
    'Dealership': name,
    'Dealer Group': 'Group Name',
    'Your New Column': 'Some value',  # ← Add data
    ...
})
```

---

## 🔍 Debugging Guide

### Debug Locally

```bash
# Run with verbose logging
streamlit run run.py --logger.level=debug

# Output shows detailed information:
# - Which strategies are tried
# - What data is extracted
# - Any errors that occur
```

### Check Railway Logs

```
Visual Guide:

1. Open: https://railway.app
   
2. Click your project

3. Click "Deployments"
   ┌──────────────────────────────┐
   │ ✓ Dec 18 - 3:04 PM          │ ← Click this
   │ ✗ Dec 18 - 2:55 PM          │
   └──────────────────────────────┘

4. View logs:
   - "Build Logs" → Shows installation
   - "Deploy Logs" → Shows startup
   - "Runtime Logs" → Shows errors
```

### Test Individual Components

Create a test script:

```python
# test_component.py

from src.services.scraper_service import ScraperService

# Test scraping
service = ScraperService()
result = service.scrape_dealer_locations(
    'Test Dealer',
    'https://example.com/locations'
)

print(f"Status: {result.status}")
print(f"Dealers: {len(result.dealers)}")
print(f"First dealer: {result.dealers[0] if result.dealers else 'None'}")
```

Run it:
```bash
python test_component.py
```

### Useful Debug Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# Check Git status
git status

# View recent commits
git log --oneline -10

# See what files changed
git diff

# Check if virtual environment is active
which python  # Mac/Linux
where python  # Windows

# Kill all Streamlit processes
pkill -f streamlit  # Mac/Linux
taskkill /F /IM streamlit.exe  # Windows
```

---

## 🆘 Getting Help

### Documentation Files

```
├── README.md                         ← Start here
├── COMPLETE_DEVELOPER_GUIDE.md       ← This file
├── DEVELOPER_SETUP.md                ← Quick setup
├── HANDOFF_EMAIL_TEMPLATE.md         ← For managers
├── PROJECT_STRUCTURE_VISUAL.md       ← Visual guide
├── SIMPLIFIED_DIAGRAM.md             ← Flow charts
└── docs/
    ├── HOW_IT_WORKS.md               ← Architecture deep dive
    ├── HANDOFF_NOTES.md              ← Maintenance guide
    └── PROJECT_STRUCTURE.md          ← Detailed structure
```

### External Resources

| Resource | Link | Purpose |
|----------|------|---------|
| Python Docs | [docs.python.org](https://docs.python.org/3/) | Python language reference |
| Streamlit Docs | [docs.streamlit.io](https://docs.streamlit.io/) | Web UI framework |
| BeautifulSoup Docs | [crummy.com/software/BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) | HTML parsing |
| Playwright Docs | [playwright.dev/python](https://playwright.dev/python/) | Browser automation |
| Railway Docs | [docs.railway.app](https://docs.railway.app/) | Hosting platform |
| Git Docs | [git-scm.com/doc](https://git-scm.com/doc) | Version control |

---

## ✅ Quick Start Checklist

Print this and check off as you go:

```
SETUP CHECKLIST:

☐ Install Python 3.10 or 3.11
☐ Install Git
☐ Clone repository: git clone https://github.com/CedmondsTH/dealer-scraper.git
☐ Navigate to project: cd dealer-scraper
☐ Create virtual environment: python -m venv venv
☐ Activate virtual environment
☐ Install dependencies: pip install -r requirements.txt
☐ Install Playwright: playwright install chromium
☐ Create .env file (even if empty)
☐ Run app: streamlit run run.py
☐ Test with Lithia Motors
☐ Verify Excel download works

OPTIONAL:
☐ Install dev tools: pip install -r requirements-dev.txt
☐ Set up VS Code
☐ Configure Git user name & email
☐ Get Railway access
☐ Get GitHub access

SUCCESS!
☐ App runs locally without errors
☐ Can extract dealerships
☐ Can download Excel files
☐ Understanding project structure
```

---

## 📞 Contact & Support

### For Technical Issues

1. **Check this guide first** - Most issues are covered
2. **Review error logs** - Error messages usually explain the problem
3. **Google the error** - Many are common Python/Streamlit issues
4. **Check GitHub Issues** - [github.com/CedmondsTH/dealer-scraper/issues](https://github.com/CedmondsTH/dealer-scraper/issues)

### For Deployment Issues

1. **Check Railway dashboard** for deployment status
2. **Review Railway logs** for error messages
3. **Verify environment variables** are set correctly
4. **Try redeploying** - Sometimes fixes transient issues

### Useful Commands Summary

```bash
# Setup
git clone https://github.com/CedmondsTH/dealer-scraper.git
cd dealer-scraper
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
playwright install chromium

# Run
streamlit run run.py

# Development
git status
git add .
git commit -m "Message"
git push origin main

# Debug
python test_script.py
pip list
git log --oneline -10

# Format
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

---

## 🎉 You're Ready!

**You now have everything you need to:**

✅ Set up the development environment  
✅ Understand the project architecture  
✅ Make code changes confidently  
✅ Debug issues effectively  
✅ Deploy to production  
✅ Add new features  

**Time Investment:**
- **Setup:** 30-60 minutes
- **Learning codebase:** 2-4 hours
- **Making first change:** 1-2 hours
- **Full proficiency:** 1-2 weeks

**Good luck and happy coding!** 🚀

---

*Last Updated: December 2025*  
*Repository: https://github.com/CedmondsTH/dealer-scraper*  
*Live App: https://dealer-scraper-production.up.railway.app/*

