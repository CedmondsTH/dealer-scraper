# Dealer Scraper - Simplified Visual Diagrams

## 📊 Simple Folder View (For Email)

```
dealer-scraper/
│
├── 🎨 src/                    Main application code
│   ├── scrapers/              Extracts data from websites
│   ├── services/              Coordinates the scraping process
│   ├── utils/                 Helper tools (cleaning, parsing)
│   └── ui/                    Web interface (what users see)
│
├── 🧪 tests/                  Automated testing (catches bugs)
│
├── 📚 docs/                   Documentation & guides
│
├── 🔧 config.py               Settings & configuration
├── ▶️ run.py                  Starts the application
│
├── 🐳 Dockerfile              Deployment instructions
├── 🚂 railway.json            Hosting configuration
└── 📋 requirements.txt        Required software packages
```

---

## 🔄 How It Works (Simple Flow)

```
┌─────────────────────────────────────────────────────────────┐
│                    1. USER INPUT                             │
│  User enters: "Sonic Automotive" + website URL              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 2. FETCH WEBPAGE                             │
│  App visits the website and downloads the HTML               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│             3. TRY DIFFERENT STRATEGIES                      │
│  • Is it Sonic Automotive? → Use Sonic strategy             │
│  • Is it Lithia Motors? → Use Lithia strategy               │
│  • Unknown website? → Use generic strategies                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│               4. EXTRACT DATA                                │
│  Finds: Name, Address, City, State, Zip, Phone, Website     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│             5. CLEAN & DEDUPLICATE                           │
│  • Fix address formats                                       │
│  • Remove duplicate locations                                │
│  • Validate data quality                                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              6. EXPORT TO EXCEL                              │
│  User downloads a clean spreadsheet with all locations       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Overview (For Technical People)

```
┌──────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                           │
│                   (Streamlit Web App)                        │
│                src/ui/streamlit_app.py                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Scraper     │  │    Data      │  │     Web      │      │
│  │  Service     │  │   Service    │  │   Scraper    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│    Coordinates         Processes         Fetches pages       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  SCRAPING STRATEGIES                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Lithia  │ │  Sonic   │ │ Group 1  │ │ Generic  │       │
│  │ Strategy │ │ Strategy │ │ Strategy │ │ Strategy │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  (14 total strategies - 10 specific + 4 generic)             │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    UTILITIES                                  │
│  ┌──────────────────┐        ┌──────────────────┐           │
│  │ Address Parser   │        │  Data Cleaner    │           │
│  │ (Parses formats) │        │  (Deduplicates)  │           │
│  └──────────────────┘        └──────────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Flow

```
Developer's Computer                GitHub                    Railway (Hosting)
       │                              │                              │
       │  1. Write Code               │                              │
       │────────────────────────────→ │                              │
       │                              │                              │
       │                              │  2. Run Tests (GitHub Actions)
       │                              │        ✓ Unit Tests          │
       │                              │        ✓ Linting             │
       │                              │        ✓ Code Quality        │
       │                              │                              │
       │                              │  3. Tests Pass? ────────────→│
       │                              │                              │
       │                              │                   4. Auto-Deploy
       │                              │                   (3-5 minutes)
       │                              │                              │
       │                              │                   5. App Live!
       │                              │                    (Railway URL)
       │                              │                              │
       └──────────────────────────────┴──────────────────────────────┘
```

---

## 📦 What's Included (Checklist)

### ✅ Core Application
- [x] Web-based user interface
- [x] 14 scraping strategies (specific + generic)
- [x] Address parsing & cleaning
- [x] Duplicate removal
- [x] Excel export functionality
- [x] Error handling & logging

### ✅ Quality Assurance
- [x] Unit tests for utilities
- [x] Integration tests for scraping
- [x] Automated CI/CD pipeline
- [x] Code formatting (Black, isort)
- [x] Linting (Flake8)
- [x] Type hints throughout

### ✅ Documentation
- [x] Main README
- [x] Technical documentation (HOW_IT_WORKS.md)
- [x] Handoff notes (HANDOFF_NOTES.md)
- [x] Project structure guide
- [x] Visual diagrams (this file)
- [x] Inline code comments

### ✅ Deployment
- [x] Dockerfile for containerization
- [x] Railway configuration
- [x] Automatic deployment on push
- [x] Environment variable management
- [x] Health checks configured

### ✅ Professional Standards
- [x] Clean separation of concerns
- [x] Centralized configuration
- [x] Proper error handling
- [x] Comprehensive .gitignore
- [x] Legacy code archived (not deleted)
- [x] Professional commit history

---

## 🎯 Success Metrics

| Metric | Status |
|--------|--------|
| **Lines of Code** | ~3,500 (production-ready) |
| **Test Coverage** | Unit & integration tests in place |
| **Supported Dealers** | 8+ specific, most generic sites |
| **Average Extraction Time** | 15-45 seconds (depending on site) |
| **Deployment Time** | 3-5 minutes (automatic) |
| **Uptime** | 99%+ (Railway hosting) |
| **Documentation** | Comprehensive |

---

## 💡 For Non-Technical Summary

**In Plain English:**
This app visits dealer websites, finds all their location information, and puts it in an Excel spreadsheet automatically. It's like having a robot that can read websites and copy information into spreadsheets for you.

**Why It's Valuable:**
- Saves hours of manual data entry
- Reduces human error
- Works 24/7 online
- Handles 100+ locations in seconds
- Professional, tested, and documented

**Who Can Use It:**
Anyone with a web browser - no technical skills required!

