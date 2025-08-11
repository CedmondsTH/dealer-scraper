# How the Dealer Scraper Works

## What This App Does

This app scrapes dealer locations from car dealership group websites and exports them to Excel. A user enters a dealer group name and URL, clicks a button, and gets back an Excel file with hundreds of dealer locations including addresses, phone numbers, and other details.

## The Big Picture

Think of this app like a smart detective that knows how to read different types of websites:

1. **User gives it a website** (like "https://www.lithia.com/locations")
2. **App figures out what type of website it is** (Lithia Motors, Group 1 Automotive, etc.)
3. **App uses the right strategy** to extract dealer information
4. **App cleans up the data** and removes duplicates
5. **User gets an Excel file** with all the dealer locations

## How It's Organized (File Structure)

```
dealer-scraper/
├── app.py                    # Main Streamlit web interface
├── src/                      # All the smart code lives here
│   ├── scrapers/            # Different strategies for different websites
│   │   ├── strategies/      # One strategy per dealer group type
│   │   ├── base_scraper.py  # Template that all strategies follow
│   │   └── strategy_manager.py # Decides which strategy to use
│   ├── services/            # Main business logic
│   │   ├── scraper_service.py  # Orchestrates the whole scraping process
│   │   ├── data_service.py     # Cleans and processes the data
│   │   └── web_scraper.py      # Fetches web pages
│   └── utils/               # Helper functions
│       ├── address_parser.py   # Figures out addresses
│       └── data_cleaner.py     # Cleans and validates data
├── assets/                   # Logo and images
└── archive/                 # Old files we don't need anymore
```

## The Smart Strategy System

The app uses a "Strategy Pattern" - basically, it has different game plans for different types of websites:

### 1. **Lithia Motors Strategy**
- Knows that Lithia stores their dealer data in a specific HTML format
- Looks for `<div class="dealer-location">` tags
- Extracts name, address, phone, etc. from specific places

### 2. **Group 1 Automotive Strategy**
- Different HTML structure than Lithia
- Looks for different CSS classes and HTML patterns
- Same end result: extracts dealer information

### 3. **JSON-LD Strategy**
- Some websites embed dealer data in JSON format
- Looks for `<script type="application/ld+json">` tags
- Parses the JSON to extract structured data

### 4. **JavaScript Variables Strategy**
- Some sites store data in JavaScript arrays
- Looks for patterns like `var locations = [...]`
- Extracts the JavaScript and parses it

### 5. **AutoCanada Strategy**
- Specific to AutoCanada website structure
- Custom parsing logic for their unique format

### 6. **Generic Strategy**
- Fallback for websites that don't match the above
- Tries common patterns and HTML structures

## How The App Decides Which Strategy To Use

The `strategy_manager.py` file contains the logic:

1. **Looks at the URL** - if it contains "lithia.com", use Lithia strategy
2. **Looks at the HTML content** - searches for specific patterns
3. **Tries strategies in order** until one finds dealer data
4. **Falls back to Generic** if nothing else works

## The Two-Step Web Scraping Approach

We use a smart hybrid approach:

### Step 1: Try Requests First (Fast & Simple)
- Uses Python's `requests` library
- Like asking "Can I please have your HTML?"
- Works for 90% of websites
- Super fast (no browser needed)

### Step 2: Fallback to Playwright (Powerful Browser)
- If requests fails, fire up a real browser
- Can handle JavaScript-heavy websites
- Slower but more capable
- Like having a robot control Chrome

## Data Processing Pipeline

Once we get the raw dealer data, we clean it up:

### 1. **Address Parsing**
- Takes messy addresses like "123 Main St, Suite 456, Anytown, CA 90210"
- Breaks it into: street, city, state, zip, country
- Handles different formats and abbreviations

### 2. **Data Validation**
- Checks if it's actually a dealership (not a corporate office)
- Validates phone numbers, addresses, etc.
- Removes obviously bad data

### 3. **Deduplication**
- Finds duplicate locations (same address, similar names)
- Keeps the most complete record
- Prevents the same dealer from appearing twice

### 4. **Data Enhancement**
- Figures out what country each dealer is in
- Extracts car brands from dealer names
- Standardizes city and state names
- Cleans up website URLs

## Error Handling

The app is built to handle things going wrong:

- **Website is down?** Try a few times, then give a helpful error
- **Weird HTML format?** Try multiple strategies
- **Network issues?** Retry with different approaches
- **No dealers found?** Tell the user clearly what happened

## Configuration

The app has smart defaults but can be configured:

- **Timeout settings** - how long to wait for websites
- **Browser settings** - headless mode, viewport size
- **Logging levels** - how much detail to show
- **Debug mode** - saves HTML files for troubleshooting

## Why This Architecture?

This isn't just thrown-together code. It's built like enterprise software:

### **Modular Design**
- Each piece has one job
- Easy to add new dealer groups
- Easy to test individual components

### **Strategy Pattern**
- Adding a new dealer group = adding one new strategy file
- Old strategies don't break when you add new ones
- Clean separation of concerns

### **Service Layer**
- Business logic is separate from UI
- Could easily add a REST API later
- Easy to test without the web interface

### **Professional Error Handling**
- Detailed logging for debugging
- Graceful failures with user-friendly messages
- Retry logic for network issues

## Adding a New Dealer Group

If you need to scrape a new dealer group:

1. **Create a new strategy file** in `src/scrapers/strategies/`
2. **Inherit from `ScraperStrategy`** base class
3. **Implement the `extract` method** with your parsing logic
4. **Register it** in `strategy_manager.py`
5. **Test it** with the new dealer group's website

That's it! The rest of the system automatically handles the new strategy.

## Maintenance

### **Websites Change**
- When a dealer group updates their website, usually only one strategy file needs updating
- Debug mode helps you see what the HTML looks like now
- The modular design means fixes are isolated

### **Adding Features**
- New data fields? Update the data models
- New validation rules? Update the data cleaner
- New UI features? Update just the Streamlit app

### **Performance Issues**
- The requests-first approach handles most performance concerns
- Caching could be added at the web scraper level
- Database storage could replace in-memory processing for huge datasets

## Common Issues & Solutions

### **"Failed to fetch page content"**
- Usually means the website is blocking automated requests
- Try updating the User-Agent string in `web_scraper.py`
- May need to add delays or proxy support

### **"No dealers found"**
- Website structure changed - check the strategy logic
- New dealer group - needs a new strategy
- Website requires JavaScript - make sure Playwright fallback works

### **"Too slow"**
- Check if Playwright is being used unnecessarily
- Add more specific URL patterns to trigger requests-first approach
- Consider adding caching

This architecture makes the app maintainable, extensible, and professional. It's built to last and grow with your needs.