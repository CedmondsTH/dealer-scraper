# 📊 Dealer Scraper - Professional Diagrams

**These diagrams will render as beautiful graphics on GitHub!**

---

## 🔄 How the App Works - User Flow

```mermaid
flowchart TD
    A[👤 User Opens Browser] --> B[🌐 Streamlit Web Interface]
    B --> C{User Enters Data}
    C --> D[Dealer Name: Sonic Automotive]
    C --> E[Website URL]
    D --> F[Click Extract Dealerships]
    E --> F
    F --> G[⚙️ Scraper Service Starts]
    G --> H[📥 Web Scraper Fetches HTML]
    H --> I{Try HTTP Request}
    I -->|Success| J[HTML Downloaded]
    I -->|Fails 403/404| K[🌐 Playwright Browser]
    K --> J
    J --> L[🎯 Strategy Selector]
    L --> M{Check Domain}
    M -->|sonicautomotive.com| N[Sonic Strategy]
    M -->|lithia.com| O[Lithia Strategy]
    M -->|Unknown| P[Generic Strategy]
    N --> Q[📊 Extract Dealer Data]
    O --> Q
    P --> Q
    Q --> R[🧹 Clean & Validate Data]
    R --> S[Remove Duplicates]
    S --> T[Parse Addresses]
    T --> U[📑 Create Excel File]
    U --> V[✅ Display Results]
    V --> W[User Downloads Excel]
    
    style A fill:#e1f5ff
    style B fill:#fff3cd
    style G fill:#d4edda
    style Q fill:#f8d7da
    style U fill:#d1ecf1
    style W fill:#d4edda
```

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[Streamlit Web App<br/>streamlit_app.py]
    end
    
    subgraph "Service Layer"
        SS[Scraper Service<br/>Coordinator]
        DS[Data Service<br/>Processing & Export]
        WS[Web Scraper<br/>HTTP Requests]
        PS[Playwright Subprocess<br/>Browser Automation]
    end
    
    subgraph "Strategy Layer"
        SM[Strategy Manager]
        
        subgraph "Specific Strategies"
            S1[Lithia]
            S2[Sonic]
            S3[Group1]
            S4[Hudson]
            S5[+4 more]
        end
        
        subgraph "Generic Strategies"
            G1[Dealer.com]
            G2[Generic HTML]
            G3[+2 more]
        end
    end
    
    subgraph "Utility Layer"
        AP[Address Parser]
        DC[Data Cleaner]
    end
    
    UI --> SS
    SS --> WS
    SS --> DS
    WS --> PS
    SS --> SM
    SM --> S1 & S2 & S3 & S4 & S5
    SM --> G1 & G2 & G3
    DS --> AP
    DS --> DC
    
    style UI fill:#e3f2fd
    style SS fill:#fff3e0
    style DS fill:#fff3e0
    style SM fill:#f3e5f5
    style S1 fill:#e8f5e9
    style S2 fill:#e8f5e9
    style G1 fill:#fff9c4
    style AP fill:#fce4ec
    style DC fill:#fce4ec
```

---

## 📦 Data Flow Process

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant SS as Scraper Service
    participant WS as Web Scraper
    participant SM as Strategy Manager
    participant STR as Strategy
    participant DC as Data Cleaner
    participant DS as Data Service
    
    User->>UI: Enter dealer name & URL
    UI->>SS: scrape_dealer_locations()
    SS->>WS: fetch_page(url)
    
    alt HTTP Success
        WS->>WS: requests.get()
        WS-->>SS: HTML content
    else HTTP Fails
        WS->>WS: Playwright browser
        WS-->>SS: HTML content
    end
    
    SS->>SM: select_strategy(html, url)
    SM->>STR: Extract with matched strategy
    STR-->>SM: Raw dealer data (142 items)
    SM-->>SS: Dealer list
    
    SS->>DC: Clean & validate data
    DC->>DC: Parse addresses
    DC->>DC: Remove duplicates
    DC-->>SS: Clean data (138 items)
    
    SS->>DS: create_dataframe()
    DS->>DS: Format columns
    DS->>DS: Generate Excel
    DS-->>SS: Excel file
    
    SS-->>UI: Results + Excel
    UI-->>User: Display & Download
```

---

## 🚀 Deployment Flow

```mermaid
graph LR
    A[💻 Developer] -->|git push| B[GitHub Repository]
    B -->|Webhook| C[GitHub Actions]
    
    C --> D{Run Tests}
    D -->|✅ Pass| E[Railway Notified]
    D -->|❌ Fail| F[Deployment Blocked]
    
    E --> G[Railway Builds]
    G --> H[Install Dependencies]
    H --> I[Install Playwright]
    I --> J[Create Container]
    J --> K[Deploy to Production]
    K --> L[Health Check]
    L -->|✅ Healthy| M[🌐 App Live]
    L -->|❌ Unhealthy| N[Rollback]
    
    M --> O[User Access]
    
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#fff9c4
    style E fill:#e8f5e9
    style G fill:#ffe0b2
    style M fill:#c8e6c9
    style O fill:#b2dfdb
```

---

## 📁 File Structure Overview

```mermaid
graph TD
    ROOT[dealer-scraper/]
    
    ROOT --> ENTRY[🎯 Entry Points]
    ROOT --> SRC[📁 src/]
    ROOT --> TESTS[🧪 tests/]
    ROOT --> DOCS[📚 docs/]
    ROOT --> DEPLOY[🐳 Deployment]
    
    ENTRY --> E1[run.py ★]
    ENTRY --> E2[config.py ★]
    ENTRY --> E3[requirements.txt]
    
    SRC --> SCRAPERS[scrapers/]
    SRC --> SERVICES[services/]
    SRC --> UTILS[utils/]
    SRC --> UI[ui/]
    
    SCRAPERS --> STRAT[strategies/<br/>14 strategies]
    SCRAPERS --> EXTRACT[extractors/]
    
    SERVICES --> SV1[scraper_service.py ★]
    SERVICES --> SV2[data_service.py ★]
    SERVICES --> SV3[web_scraper.py]
    
    UTILS --> U1[address_parser.py]
    UTILS --> U2[data_cleaner.py]
    
    UI --> UI1[streamlit_app.py ★]
    
    DEPLOY --> D1[Dockerfile]
    DEPLOY --> D2[railway.json]
    DEPLOY --> D3[start.sh]
    
    style ROOT fill:#e3f2fd
    style SRC fill:#fff3e0
    style SCRAPERS fill:#f3e5f5
    style SERVICES fill:#e8f5e9
    style UTILS fill:#fff9c4
    style UI fill:#ffe0b2
```

---

## 🔀 Strategy Selection Logic

```mermaid
flowchart TD
    START[HTML Content Received] --> CHECK{Check URL Domain}
    
    CHECK -->|sonicautomotive.com| S1[Sonic Strategy]
    CHECK -->|lithia.com| S2[Lithia Strategy]
    CHECK -->|group1auto.com| S3[Group1 Strategy]
    CHECK -->|hudsonauto.com| S4[Hudson Strategy]
    CHECK -->|autocanada.ca| S5[AutoCanada Strategy]
    CHECK -->|cooperauto.com| S6[Cooper Strategy]
    CHECK -->|courtesyauto.com| S7[Courtesy Strategy]
    CHECK -->|rayskillman.com| S8[Ray Skillman Strategy]
    
    S1 --> EXTRACT[Extract Data]
    S2 --> EXTRACT
    S3 --> EXTRACT
    S4 --> EXTRACT
    S5 --> EXTRACT
    S6 --> EXTRACT
    S7 --> EXTRACT
    S8 --> EXTRACT
    
    CHECK -->|Unknown Domain| GENERIC{Try Generic}
    
    GENERIC --> G1[Dealer.com Strategy]
    GENERIC --> G2[Generic HTML Strategy]
    GENERIC --> G3[DealerOn Strategy]
    
    G1 -->|Match| EXTRACT
    G2 -->|Match| EXTRACT
    G3 -->|Match| EXTRACT
    
    G1 -->|No Match| FALLBACK
    G2 -->|No Match| FALLBACK
    G3 -->|No Match| FALLBACK
    
    FALLBACK[Fallback Strategies] --> F1[JSON-LD]
    FALLBACK --> F2[JavaScript]
    FALLBACK --> F3[AI/LLM]
    
    F1 --> EXTRACT
    F2 --> EXTRACT
    F3 --> EXTRACT
    
    EXTRACT --> RETURN[Return Dealer Data]
    
    style START fill:#e1f5ff
    style CHECK fill:#fff3cd
    style S1 fill:#d4edda
    style S2 fill:#d4edda
    style GENERIC fill:#fff3cd
    style FALLBACK fill:#f8d7da
    style EXTRACT fill:#d1ecf1
    style RETURN fill:#d4edda
```

---

## 📊 Component Dependencies

```mermaid
graph TD
    User -->|Uses| UI[Streamlit UI]
    UI -->|Calls| SS[Scraper Service]
    
    SS -->|Fetches Pages| WS[Web Scraper]
    SS -->|Processes Results| DS[Data Service]
    
    WS -->|Fallback| PS[Playwright]
    
    SS -->|Delegates To| SM[Strategy Manager]
    
    SM -->|Selects| STRAT[Strategies]
    
    STRAT -->|Uses| EXT[Extractors]
    
    DS -->|Uses| AP[Address Parser]
    DS -->|Uses| DC[Data Cleaner]
    
    UI -->|Reads| CFG[Config]
    SS -->|Reads| CFG
    STRAT -->|Reads| CFG
    
    STRAT -->|Stores Patterns| RULES[Rules JSON]
    
    style User fill:#e3f2fd
    style UI fill:#bbdefb
    style SS fill:#c5e1a5
    style WS fill:#fff9c4
    style DS fill:#ffccbc
    style STRAT fill:#f8bbd0
    style CFG fill:#b2dfdb
```

---

## 🎯 Scraping Success Flow

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize --> FetchHTML
    
    FetchHTML --> TryHTTP
    TryHTTP --> HTTPSuccess: 200 OK
    TryHTTP --> TryPlaywright: 403/404/Timeout
    
    TryPlaywright --> PlaywrightSuccess
    TryPlaywright --> Failed: Error
    
    HTTPSuccess --> SelectStrategy
    PlaywrightSuccess --> SelectStrategy
    
    SelectStrategy --> SpecificStrategy: Domain Match
    SelectStrategy --> GenericStrategy: No Match
    
    SpecificStrategy --> ExtractData
    GenericStrategy --> ExtractData
    GenericStrategy --> FallbackStrategy: No Data
    
    FallbackStrategy --> ExtractData
    FallbackStrategy --> Failed: No Data
    
    ExtractData --> ValidateData
    ValidateData --> CleanData: Valid
    ValidateData --> Failed: Invalid
    
    CleanData --> DeduplicateData
    DeduplicateData --> FormatExcel
    FormatExcel --> Success
    
    Failed --> [*]
    Success --> [*]
```

---

## 💾 Data Structure Flow

```mermaid
graph LR
    subgraph Input
        A[Raw HTML]
    end
    
    subgraph Extraction
        B[Strategy Extracts]
        C[Raw Dictionaries]
    end
    
    subgraph Cleaning
        D[Validate Fields]
        E[Parse Addresses]
        F[Remove Duplicates]
    end
    
    subgraph Formatting
        G[pandas DataFrame]
        H[Add Columns]
        I[Sort & Order]
    end
    
    subgraph Output
        J[Excel File]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    
    style A fill:#ffebee
    style C fill:#fff3e0
    style F fill:#e8f5e9
    style G fill:#e3f2fd
    style J fill:#f3e5f5
```

---

## 📝 Notes

**Viewing These Diagrams:**

1. **On GitHub:** These diagrams render automatically as beautiful graphics
2. **In VS Code:** Install "Markdown Preview Mermaid Support" extension
3. **Export as Images:** Use GitHub's export feature or Mermaid Live Editor

**Editing Diagrams:**

- Diagrams are in Mermaid syntax (text-based)
- Easy to edit and update
- Can be version controlled
- GitHub renders them beautifully

**Links:**
- Mermaid Documentation: https://mermaid.js.org/
- Mermaid Live Editor: https://mermaid.live/
- Export as PNG/SVG from GitHub or Mermaid Live

---

**These diagrams provide visual representations of:**
✅ User interaction flow  
✅ System architecture  
✅ Data processing pipeline  
✅ Deployment workflow  
✅ File structure  
✅ Strategy selection logic  
✅ Component dependencies  
✅ State transitions  
✅ Data transformations  

