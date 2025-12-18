# Dealer Scraper - Developer Setup Guide

## 📋 Tech Stack Overview

### **Required Technologies**

To work on this project, you need access to and knowledge of:

| Technology | Version | Purpose | Installation Link |
|------------|---------|---------|-------------------|
| **Python** | 3.10 or 3.11 | Programming language | [python.org](https://www.python.org/downloads/) |
| **Git** | Latest | Version control | [git-scm.com](https://git-scm.com/) |
| **GitHub** | Account | Code repository | [github.com](https://github.com/) |
| **Railway** | Account | Hosting/deployment | [railway.app](https://railway.app/) |
| **VS Code** (recommended) | Latest | Code editor | [code.visualstudio.com](https://code.visualstudio.com/) |

### **Python Packages (Auto-installed)**

These are installed automatically via `requirements.txt`:

**Core Dependencies:**
- `pandas` - Data manipulation
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast HTML parser
- `requests` - HTTP requests
- `streamlit` - Web UI framework
- `playwright` - Browser automation (JavaScript-heavy sites)
- `openpyxl` - Excel file creation
- `python-dotenv` - Environment variables

**Development Tools** (optional, from `requirements-dev.txt`):
- `pytest` - Testing framework
- `black` - Code formatter
- `flake8` - Linting
- `mypy` - Type checking
- `isort` - Import sorting

### **Browser Dependencies**

Playwright requires Chromium to be installed (happens automatically during setup).

---

## 🚀 Setup From Scratch (Step-by-Step)

### **Step 1: Install Python**

1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: During installation, check "Add Python to PATH"
3. Verify installation:
   ```bash
   python --version
   # Should show: Python 3.11.x
   ```

### **Step 2: Install Git**

1. Download Git from [git-scm.com](https://git-scm.com/)
2. Install with default settings
3. Verify installation:
   ```bash
   git --version
   # Should show: git version 2.x.x
   ```

### **Step 3: Clone the Repository**

```bash
# Clone the repo
git clone https://github.com/CedmondsTH/dealer-scraper.git

# Navigate into the project
cd dealer-scraper

# Verify you're on the main branch
git branch
# Should show: * main
```

### **Step 4: Set Up Python Environment**

**Option A: Using Virtual Environment (Recommended)**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

**Option B: Using System Python**

Skip virtual environment (not recommended for production, but works).

### **Step 5: Install Dependencies**

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional, for testing/linting)
pip install -r requirements-dev.txt

# Install Playwright browser
playwright install chromium
```

**Expected output:** You should see packages installing. This takes 2-5 minutes.

### **Step 6: Set Up Environment Variables**

Create a `.env` file in the project root:

```bash
# Create .env file
# On Windows:
type nul > .env

# On Mac/Linux:
touch .env
```

Add these variables to `.env`:

```env
# Optional: Gemini API key for AI fallback (not required for basic functionality)
GEMINI_API_KEY=your_key_here_if_you_have_one

# Optional: OpenAI API key for AI fallback (not required for basic functionality)
OPENAI_API_KEY=your_key_here_if_you_have_one
```

**Note:** The app works fine without these API keys - they're only for experimental AI fallback features.

### **Step 7: Run the Application Locally**

```bash
# Start the Streamlit app
streamlit run run.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

**Your browser should automatically open to the app!**

### **Step 8: Test It Works**

1. In the app, enter:
   - **Dealer Name:** Lithia Motors
   - **Website URL:** https://www.lithia.com/locations.htm
2. Click "Extract Dealerships"
3. You should see 200+ dealerships extracted
4. Download the Excel file

**If this works, you're all set!** ✅

---

## 🔧 Development Workflow

### **Making Code Changes**

```bash
# 1. Make sure you're on main branch
git checkout main

# 2. Pull latest changes
git pull origin main

# 3. Create a new branch (optional but recommended)
git checkout -b feature/your-feature-name

# 4. Make your code changes

# 5. Test locally
streamlit run run.py

# 6. Run tests (if available)
pytest tests/

# 7. Format code
black src/ tests/
isort src/ tests/

# 8. Stage changes
git add .

# 9. Commit
git commit -m "Description of your changes"

# 10. Push to GitHub
git push origin main
# (or push to your feature branch and create a pull request)
```

### **Automatic Deployment**

When you push to `main` branch:
1. GitHub Actions runs automatic tests
2. If tests pass, Railway automatically deploys
3. Takes 3-5 minutes to go live
4. Check https://dealer-scraper-production.up.railway.app/

---

## 🐛 Top 5 Issues & Fixes

### **Issue #1: "ModuleNotFoundError: No module named 'X'"**

**Symptom:** 
```
ModuleNotFoundError: No module named 'streamlit'
```

**Cause:** Dependencies not installed or wrong Python environment

**Fix:**
```bash
# Make sure virtual environment is activated (if using one)
# On Windows:
venv\Scripts\activate

# Install dependencies again
pip install -r requirements.txt

# Verify installation
pip list | grep streamlit
```

---

### **Issue #2: "playwright: command not found" or Browser Errors**

**Symptom:**
```
Error: Chromium browser not found
```

**Cause:** Playwright browsers not installed

**Fix:**
```bash
# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium

# Install system dependencies (might be needed on Linux)
playwright install-deps chromium
```

---

### **Issue #3: App Won't Start Locally**

**Symptom:**
```
Error: File does not exist: run.py
```

**Cause:** Not in the correct directory

**Fix:**
```bash
# Navigate to project root
cd dealer-scraper

# Verify you're in the right place
ls
# Should see: run.py, src/, tests/, README.md, etc.

# Now run the app
streamlit run run.py
```

---

### **Issue #4: "Port 8501 is already in use"**

**Symptom:**
```
OSError: [Errno 48] Address already in use
```

**Cause:** Another Streamlit instance is running

**Fix:**

**Option A: Use a different port**
```bash
streamlit run run.py --server.port 8502
```

**Option B: Kill the existing process**
```bash
# On Windows:
taskkill /F /IM streamlit.exe

# On Mac/Linux:
pkill -f streamlit
```

---

### **Issue #5: Railway Deployment Fails**

**Symptom:** Railway dashboard shows "Deployment failed" or app crashes

**Common Causes & Fixes:**

**A. Missing Package in requirements.txt**
```bash
# If you added a new package, make sure it's in requirements.txt
pip freeze | grep package-name

# Add it manually to requirements.txt
echo "package-name==version" >> requirements.txt

# Push to GitHub
git add requirements.txt
git commit -m "Add missing package"
git push origin main
```

**B. Environment Variables Missing**
- Go to Railway dashboard
- Click on your project → Variables
- Add any missing environment variables
- Redeploy

**C. Build Timeout**
- Railway has a 10-minute build limit
- Usually means Playwright installation is slow
- Solution: This is already optimized in Dockerfile, just redeploy

**D. Port Configuration Issues**
- Make sure `start.sh` is executable: `chmod +x start.sh`
- Verify Railway is setting the `PORT` environment variable
- Check `railway.json` configuration is correct

**Fix for Railway Port Issues:**
```bash
# Verify start.sh has correct permissions
git update-index --chmod=+x start.sh
git commit -m "Make start.sh executable"
git push origin main
```

---

## 🔍 Debugging Tips

### **Check Logs Locally**

```bash
# Run with verbose logging
streamlit run run.py --logger.level=debug
```

### **Check Logs on Railway**

1. Go to Railway dashboard
2. Click your project
3. Click "Deployments"
4. Click the latest deployment
5. View "Deploy Logs" or "Runtime Logs"

### **Test Individual Components**

```python
# Create a test script: test_scraping.py
from src.services.scraper_service import ScraperService

service = ScraperService()
result = service.scrape_dealer_locations(
    'Lithia Motors', 
    'https://www.lithia.com/locations.htm'
)

print(f"Status: {result.status}")
print(f"Dealers found: {len(result.dealers)}")
print(f"First dealer: {result.dealers[0] if result.dealers else 'None'}")
```

Run it:
```bash
python test_scraping.py
```

---

## 📚 Project Structure Quick Reference

```
Key Files for Developers:

src/
├── scrapers/strategies/     ← Add new dealer-specific strategies here
├── services/
│   └── scraper_service.py   ← Main scraping coordinator
├── ui/
│   └── streamlit_app.py     ← UI changes go here
└── utils/
    ├── address_parser.py    ← Address parsing logic
    └── data_cleaner.py      ← Deduplication logic

tests/                       ← Add tests here
config.py                    ← Change timeouts, settings here
requirements.txt             ← Add new packages here
```

---

## 🎯 Common Development Tasks

### **Add Support for a New Dealer Group**

1. Create a new strategy file:
   ```bash
   touch src/scrapers/strategies/new_dealer_strategy.py
   ```

2. Copy template from an existing strategy (e.g., `lithia_strategy.py`)

3. Implement the `can_handle()` and `extract_dealers()` methods

4. Register the strategy in `src/scrapers/strategy_manager.py`:
   ```python
   from src.scrapers.strategies.new_dealer_strategy import NewDealerStrategy
   
   scraper_registry.register(NewDealerStrategy())
   ```

5. Test locally with the dealer's website

### **Change Timeout Settings**

Edit `config.py`:
```python
class WebScraperConfig:
    timeout: int = 30  # Change to 60 for slower sites
```

### **Change UI Text**

Edit `src/ui/streamlit_app.py`:
```python
st.title("Dealer Scraper")  # Change this
```

### **Add a New Output Field**

1. Edit `config.py`:
   ```python
   OUTPUT_COLUMNS: List[str] = [
       "Dealership", "Dealer Group", 
       "Your New Field",  # Add here
       "Address", ...
   ]
   ```

2. Ensure your scrapers return the new field in their data dictionaries

---

## 🆘 Getting Help

### **Documentation Files**

- `README.md` - Project overview
- `docs/HOW_IT_WORKS.md` - Technical architecture
- `docs/HANDOFF_NOTES.md` - Maintenance guide
- `PROJECT_STRUCTURE_VISUAL.md` - Visual structure guide

### **Useful Commands**

```bash
# Check Python version
python --version

# Check installed packages
pip list

# See Git status
git status

# See recent commits
git log --oneline -10

# Run tests
pytest tests/ -v

# Format all code
black src/ tests/
isort src/ tests/

# Check for linting issues
flake8 src/ tests/ --max-line-length=120
```

### **External Resources**

- Python Docs: https://docs.python.org/3/
- Streamlit Docs: https://docs.streamlit.io/
- BeautifulSoup Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Playwright Docs: https://playwright.dev/python/
- Railway Docs: https://docs.railway.app/

---

## ✅ Setup Checklist

Use this to verify your setup is complete:

- [ ] Python 3.10 or 3.11 installed
- [ ] Git installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] `requirements.txt` packages installed
- [ ] Playwright Chromium browser installed
- [ ] App runs locally (`streamlit run run.py`)
- [ ] Can extract dealerships from Lithia Motors test
- [ ] GitHub account has access to repository
- [ ] Railway account has access to project (if deploying)
- [ ] `.env` file created (even if empty)

---

## 🚨 Important Notes

1. **Never commit `.env` files** - They contain sensitive API keys
2. **Always test locally before pushing** - Saves time and Railway build minutes
3. **Keep virtual environment activated** - Ensures consistent dependencies
4. **Pull before you push** - Avoids merge conflicts
5. **Railway automatically deploys from `main`** - Test thoroughly first!

---

## 📞 Quick Start Summary

```bash
# 1. Clone & navigate
git clone https://github.com/CedmondsTH/dealer-scraper.git
cd dealer-scraper

# 2. Set up environment
python -m venv venv
venv\Scripts\activate  # Windows
# OR: source venv/bin/activate  # Mac/Linux

# 3. Install everything
pip install -r requirements.txt
playwright install chromium

# 4. Run the app
streamlit run run.py

# 5. Open browser to: http://localhost:8501
```

**That's it! You're ready to develop.** 🎉

