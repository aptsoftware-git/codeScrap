# Simplified Architecture and Design Document

## Event-Focused Web Scraping, Summarization & Export Tool (v1.0 - Simplified)

---

## Document Information

**Version:** 1.0 - Simplified (No Database, No Authentication)  
**Last Updated:** November 2025  
**Status:** Design Phase  
**Related Documents:** WebScraperRequirementDocument.md

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [Component Design](#4-component-design)
5. [Data Models](#5-data-models)
6. [API Design](#6-api-design)
7. [File Storage Strategy](#7-file-storage-strategy)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Development Guidelines](#9-development-guidelines)
10. [Implementation Phases](#10-implementation-phases)

---

## 1. Executive Summary

This document outlines a **simplified architecture** for an event-focused web scraping tool that:
- Scrapes content from configurable news sources
- Uses Ollama LLMs for event extraction and summarization
- Provides a web interface for querying and reviewing events
- **Stores all data in-memory during session**
- **Exports results directly to Excel files**
- **No database required**
- **No authentication required**

### 1.1 Key Simplifications

✅ **No Database:** All data stored in memory during runtime  
✅ **No Authentication:** Open access (suitable for internal/local use)  
✅ **Direct Excel Export:** Primary storage mechanism  
✅ **Session-based:** Each search is independent  
✅ **Stateless API:** No persistent user sessions  
✅ **Simplified Deployment:** Fewer moving parts  

### 1.2 Architecture Philosophy

- **Single-session workflow:** User initiates search → scrape → process → review → export
- **Ephemeral data:** Results exist only during the session
- **Excel as database:** Historical data stored in Excel files
- **Minimal infrastructure:** Focus on core scraping and LLM processing

---

## 2. Technology Stack

### 2.1 Backend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI | REST API, async support, simple & fast |
| Web Scraping | BeautifulSoup4, Requests | HTML parsing, HTTP requests |
| HTTP Client | httpx | Async HTTP requests with connection pooling |
| NLP/NER | spaCy | Named entity recognition |
| LLM Integration | Ollama Python SDK | Local LLM for summarization & extraction |
| Excel Export | openpyxl | Generate .xlsx files |
| Configuration | YAML + pydantic | Source configuration management |
| Validation | pydantic | Data validation |
| Caching | In-memory dict/LRU cache | Optional response caching |

**Removed from original design:**
- ❌ Database (PostgreSQL)
- ❌ ORM (SQLAlchemy)
- ❌ Task Queue (Celery)
- ❌ Message Broker (Redis)
- ❌ Authentication system

### 2.2 Frontend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 18 | UI component library |
| Language | TypeScript | Type safety |
| UI Library | Material-UI (MUI) | Pre-built components |
| State Management | React Context + useState | Simple state management |
| HTTP Client | Axios | API communication |
| Date Handling | date-fns | Date manipulation |
| Routing | React Router | Client-side routing |

**Removed from original design:**
- ❌ Complex state management (Redux/Zustand)
- ❌ Server state caching (React Query)

### 2.3 DevOps & Infrastructure

- **Logging:** Python logging + Loguru
- **Testing:** pytest, React Testing Library
- **Deployment:** Local development setup (native installation)

### 2.4 Ollama Configuration

**Model Selection (choose based on your needs):**

| Model | Parameters | Speed | Accuracy | RAM Required | Best For |
|-------|-----------|-------|----------|--------------|----------|
| `phi3:mini` | ~3.8B | ⚡⚡⚡ | ⭐⭐ | 2-3GB | High-volume, simple events |
| `llama3.1:8b` | 8B | ⚡⚡ | ⭐⭐⭐ | 4-6GB | Balanced performance |
| `mistral:7b` | 7B | ⚡⚡ | ⭐⭐⭐ | 4-6GB | Alternative to llama3.1 |
| `gpt-oss:20b` | 20B | ⚡ | ⭐⭐⭐⭐ | 12-16GB | **High accuracy, research use** |
| `llama3.1:70b` | 70B | 🐌 | ⭐⭐⭐⭐⭐ | 40GB+ | Maximum accuracy (GPU required) |

**Recommendation:** 
- **For this project**: `gpt-oss:20b` (if already installed) or `llama3.1:8b`
- **Model is configurable** via environment variable - no code changes needed

---

## 3. System Architecture

### 3.1 High-Level Architecture (Simplified)

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        React Frontend (Web Browser)                       │  │
│  │  - Search Form                                            │  │
│  │  - Results Display                                        │  │
│  │  - Excel Export Button                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTPS/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                          │  │
│  │  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │ Search         │  │ Sources      │  │ Export       │ │  │
│  │  │ Endpoint       │  │ Config       │  │ Endpoint     │ │  │
│  │  └────────────────┘  └──────────────┘  └──────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           In-Memory Session Store                         │  │
│  │  - Current search results                                 │  │
│  │  - Scraped articles cache                                 │  │
│  │  - Processed events                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Scraper    │  │   Event      │  │   Summarization      │ │
│  │   Service    │  │   Extractor  │  │   Service            │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   NLP/NER    │  │   Export     │  │   Config             │ │
│  │   Service    │  │   Service    │  │   Manager            │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Ollama LLM  │  │  File        │  │   Web Sources        │ │
│  │   Server     │  │  System      │  │   (News Sites)       │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Simplified Component Interaction Flow

#### Single Search Session Flow
```
1. User enters query → FastAPI Search endpoint
2. API loads source configuration from YAML
3. Scraper fetches configured URLs (synchronously or async)
4. Content Extractor parses HTML → Raw articles
5. NLP Service extracts entities from articles
6. Ollama LLM processes each article:
   - Classifies event type
   - Extracts structured data
   - Generates summary
7. Query Matcher filters events by relevance
8. Results stored in memory (session)
9. Results returned to frontend
10. User reviews results
11. User selects events → Export endpoint
12. Excel file generated and downloaded
13. Session data can be cleared
```

---

## 4. Component Design

### 4.1 Web Scraper Service

**Responsibility:** Fetch and parse content from configured URLs

#### 4.1.1 ScraperManager
```python
class ScraperManager:
    """Orchestrates scraping across multiple sources"""
    
    def __init__(self):
        self.rate_limiters = {}  # domain -> RateLimiter
        self.session = httpx.AsyncClient(timeout=30.0)
        
    async def scrape_sources(self, source_configs: List[SourceConfig]) -> List[ScrapedArticle]:
        """
        Scrape multiple sources with rate limiting
        Returns: List of scraped articles
        """
        articles = []
        for source in source_configs:
            if source.enabled:
                source_articles = await self.scrape_single_source(source)
                articles.extend(source_articles)
        return articles
        
    async def scrape_single_source(self, source: SourceConfig) -> List[ScrapedArticle]:
        """Scrape a single source with retry logic"""
        # Check rate limit
        # Fetch URL
        # Parse content
        # Return articles
```

#### 4.1.2 ContentExtractor
```python
class ContentExtractor:
    """Extract structured content from HTML"""
    
    def extract(self, html: str, url: str, selectors: Optional[dict] = None) -> ArticleContent:
        """
        Extract article content using BeautifulSoup
        
        Args:
            html: Raw HTML content
            url: Source URL
            selectors: Optional CSS selectors for specific sites
            
        Returns:
            ArticleContent with title, text, date
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        if selectors:
            # Use custom selectors
            title = self._extract_with_selector(soup, selectors.get('title'))
            content = self._extract_with_selector(soup, selectors.get('content'))
            date = self._extract_with_selector(soup, selectors.get('date'))
        else:
            # Generic extraction
            title = self._extract_generic_title(soup)
            content = self._extract_generic_content(soup)
            date = self._extract_generic_date(soup)
            
        return ArticleContent(
            url=url,
            title=title,
            content=self.clean_content(content),
            publication_date=date
        )
```

### 4.2 NLP Service

**Responsibility:** Named entity recognition and text preprocessing

#### 4.2.1 EntityExtractor
```python
class EntityExtractor:
    """Extract named entities using spaCy"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")  # Or en_core_web_lg for better accuracy
        
    def extract_entities(self, text: str) -> ExtractedEntities:
        """
        Extract persons, organizations, locations, dates
        
        Returns:
            ExtractedEntities with categorized entities
        """
        doc = self.nlp(text)
        
        persons = []
        organizations = []
        locations = []
        dates = []
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                persons.append(ent.text)
            elif ent.label_ == "ORG":
                organizations.append(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                locations.append(ent.text)
            elif ent.label_ == "DATE":
                dates.append(ent.text)
                
        return ExtractedEntities(
            persons=list(set(persons)),
            organizations=list(set(organizations)),
            locations=list(set(locations)),
            dates=list(set(dates))
        )
```

### 4.3 Event Extraction Service (Ollama Integration)

**Responsibility:** Use LLM to identify, classify, and extract event information

#### 4.3.1 OllamaClient
```python
import ollama
from typing import Optional, Dict, Any

class OllamaClient:
    """Wrapper for Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3.1:8b"):
        self.base_url = base_url
        self.default_model = default_model
        self.client = ollama.Client(host=base_url)
        
    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate completion from Ollama
        
        Args:
            prompt: Input prompt
            model: Model name (uses default if None)
            
        Returns:
            Generated text
        """
        model = model or self.default_model
        response = self.client.generate(model=model, prompt=prompt)
        return response['response']
        
    def generate_json(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate structured JSON output
        
        Args:
            prompt: Input prompt requesting JSON output
            model: Model name
            
        Returns:
            Parsed JSON dictionary
        """
        response_text = self.generate(prompt, model)
        # Extract JSON from response (handle markdown code blocks)
        json_text = self._extract_json(response_text)
        return json.loads(json_text)
        
    def _extract_json(self, text: str) -> str:
        """Extract JSON from markdown code blocks if present"""
        # Remove ```json and ``` markers if present
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        return text.strip()
```

#### 4.3.2 EventExtractor
```python
class EventExtractor:
    """Extract and classify events using Ollama"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        
    def extract_event_data(self, article: ArticleContent, entities: ExtractedEntities) -> EventData:
        """
        Extract all structured event data in one LLM call
        
        Args:
            article: Scraped article content
            entities: Pre-extracted entities from spaCy
            
        Returns:
            EventData with all fields populated
        """
        prompt = self._build_extraction_prompt(article, entities)
        
        try:
            result = self.ollama.generate_json(prompt)
            return self._parse_event_data(result)
        except Exception as e:
            logger.error(f"Event extraction failed: {e}")
            return self._create_fallback_event_data(article, entities)
            
    def _build_extraction_prompt(self, article: ArticleContent, entities: ExtractedEntities) -> str:
        """Build comprehensive extraction prompt"""
        return f"""
You are an expert analyst extracting structured information from news articles.

Article Title: {article.title}
Article Text: {article.content[:2000]}  # Truncate if too long

Pre-identified entities:
- People: {', '.join(entities.persons[:10])}
- Organizations: {', '.join(entities.organizations[:10])}
- Locations: {', '.join(entities.locations[:10])}
- Dates: {', '.join(entities.dates[:5])}

Extract the following information about the MAIN event described:

1. Event Type: Choose ONE from [protest, attack, bombing, cyber_attack, accident, 
   natural_disaster, conference, meeting, arrest, theft, other]

2. Perpetrator: Individual, group, or organization responsible. 
   Write "Unknown" if not mentioned or not applicable.

3. Location: 
   - City (if mentioned)
   - Region/State (if mentioned)
   - Country (if mentioned)

4. Date: Event date in YYYY-MM-DD format (use article date if event date not specified)

5. Time: Time of day in HH:MM format (write "Not specified" if not mentioned)

6. Individuals: List key people involved (max 5, comma-separated)

7. Organizations: List organizations involved (max 5, comma-separated)

8. Summary: Write a 2-4 sentence summary focusing on: what happened, where, when, who was involved.

Respond ONLY with valid JSON in this exact format:
{{
  "event_type": "",
  "perpetrator": "",
  "location": {{
    "city": "",
    "region": "",
    "country": ""
  }},
  "event_date": "",
  "event_time": "",
  "individuals": [],
  "organizations": [],
  "summary": "",
  "confidence": 0.85
}}
"""
```

#### 4.3.3 EventSummarizer (Standalone)
```python
class EventSummarizer:
    """Generate concise summaries using Ollama"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        
    def summarize(self, article: ArticleContent) -> str:
        """
        Generate 2-4 sentence summary
        
        Args:
            article: Article to summarize
            
        Returns:
            Summary text (max 800 chars)
        """
        prompt = f"""
Summarize the following news article in 2-4 sentences. Focus on:
1. What happened (the main event)
2. Where it happened
3. When it happened
4. Who was involved

Keep the summary concise and factual.

Article: {article.content[:3000]}

Summary:
"""
        summary = self.ollama.generate(prompt, model="llama3.1:8b")
        return summary.strip()[:800]  # Enforce max length
```

### 4.4 Query Matching Service

**Responsibility:** Match events against user queries and filters

#### 4.4.1 QueryMatcher
```python
class QueryMatcher:
    """Match and rank events based on user query"""
    
    def match_events(self, events: List[Event], query: SearchQuery) -> List[Event]:
        """
        Filter and rank events by relevance to query
        
        Args:
            events: List of extracted events
            query: User search query with filters
            
        Returns:
            Filtered and ranked events
        """
        filtered = []
        
        for event in events:
            score = self._calculate_relevance_score(event, query)
            if score > 0.3:  # Threshold
                event.relevance_score = score
                filtered.append(event)
                
        # Sort by relevance
        filtered.sort(key=lambda e: e.relevance_score, reverse=True)
        return filtered
        
    def _calculate_relevance_score(self, event: Event, query: SearchQuery) -> float:
        """Calculate relevance score (0-1)"""
        score = 0.0
        
        # Text matching (keyword overlap)
        text_score = self._text_similarity(query.phrase, event.summary + " " + event.title)
        score += text_score * 0.4
        
        # Location matching
        if query.location:
            location_score = self._location_match(query.location, event.location)
            score += location_score * 0.3
            
        # Date matching
        if query.date_from or query.date_to:
            date_score = self._date_match(query, event.event_date)
            score += date_score * 0.2
            
        # Event type matching
        if query.event_type and query.event_type == event.event_type:
            score += 0.1
            
        return min(score, 1.0)
        
    def _text_similarity(self, query: str, text: str) -> float:
        """Simple keyword-based similarity"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words:
            return 0.0
            
        overlap = len(query_words & text_words)
        return overlap / len(query_words)
```

### 4.5 Export Service

**Responsibility:** Generate Excel files from events

#### 4.5.1 ExcelExporter
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from io import BytesIO

class ExcelExporter:
    """Generate Excel files from events"""
    
    def export_events(self, events: List[Event], filename: str = "events.xlsx") -> bytes:
        """
        Generate Excel file from events
        
        Args:
            events: List of events to export
            filename: Output filename (for metadata)
            
        Returns:
            Excel file as bytes
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Events"
        
        # Define headers
        headers = [
            "Event Title",
            "Summary",
            "Event Type",
            "Perpetrator",
            "Location (Full)",
            "City",
            "Region/State",
            "Country",
            "Event Date",
            "Event Time",
            "Individuals Involved",
            "Organizations Involved",
            "Source Name",
            "Source URL",
            "Publication Date",
            "Confidence Score"
        ]
        
        # Write headers
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(bold=True, size=11)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            
        # Write data
        for row_num, event in enumerate(events, 2):
            ws.cell(row=row_num, column=1, value=event.title)
            ws.cell(row=row_num, column=2, value=event.summary)
            ws.cell(row=row_num, column=3, value=event.event_type)
            ws.cell(row=row_num, column=4, value=event.perpetrator or "Unknown")
            ws.cell(row=row_num, column=5, value=event.location_full)
            ws.cell(row=row_num, column=6, value=event.location.city)
            ws.cell(row=row_num, column=7, value=event.location.region)
            ws.cell(row=row_num, column=8, value=event.location.country)
            ws.cell(row=row_num, column=9, value=event.event_date)
            ws.cell(row=row_num, column=10, value=event.event_time)
            ws.cell(row=row_num, column=11, value=", ".join(event.individuals))
            ws.cell(row=row_num, column=12, value=", ".join(event.organizations))
            ws.cell(row=row_num, column=13, value=event.source_name)
            ws.cell(row=row_num, column=14, value=event.source_url)
            ws.cell(row=row_num, column=15, value=event.publication_date)
            ws.cell(row=row_num, column=16, value=event.confidence)
            
        # Auto-adjust column widths
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 20
            
        # Make summary column wider
        ws.column_dimensions['B'].width = 50
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
```

### 4.6 Configuration Manager

**Responsibility:** Load and manage source configurations from YAML

#### 4.6.1 ConfigManager
```python
import yaml
from pathlib import Path

class ConfigManager:
    """Manage source configurations"""
    
    def __init__(self, config_path: str = "config/sources.yaml"):
        self.config_path = Path(config_path)
        self._sources = None
        
    def load_sources(self) -> List[SourceConfig]:
        """Load source configurations from YAML"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)
            
        sources = []
        for source_data in data.get('sources', []):
            sources.append(SourceConfig(**source_data))
            
        self._sources = sources
        return sources
        
    def get_enabled_sources(self) -> List[SourceConfig]:
        """Get only enabled sources"""
        if self._sources is None:
            self.load_sources()
        return [s for s in self._sources if s.enabled]
```

---

## 5. Data Models

### 5.1 Pydantic Models

```python
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime, date
from typing import Optional, List, Dict
from enum import Enum

class EventType(str, Enum):
    """Enumeration of event types"""
    PROTEST = "protest"
    ATTACK = "attack"
    BOMBING = "bombing"
    CYBER_ATTACK = "cyber_attack"
    ACCIDENT = "accident"
    NATURAL_DISASTER = "natural_disaster"
    CONFERENCE = "conference"
    MEETING = "meeting"
    ARREST = "arrest"
    THEFT = "theft"
    OTHER = "other"

class Location(BaseModel):
    """Location data"""
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    
    @property
    def full_text(self) -> str:
        """Get full location text"""
        parts = [p for p in [self.city, self.region, self.country] if p]
        return ", ".join(parts) if parts else "Unknown"

class ExtractedEntities(BaseModel):
    """Entities extracted by spaCy"""
    persons: List[str] = []
    organizations: List[str] = []
    locations: List[str] = []
    dates: List[str] = []

class ArticleContent(BaseModel):
    """Scraped article content"""
    url: str
    title: str
    content: str
    publication_date: Optional[datetime] = None
    source_name: str
    scraped_at: datetime = Field(default_factory=datetime.now)

class EventData(BaseModel):
    """Structured event data extracted by LLM"""
    event_type: EventType
    perpetrator: Optional[str] = "Unknown"
    location: Location
    event_date: Optional[date] = None
    event_time: Optional[str] = "Not specified"
    individuals: List[str] = []
    organizations: List[str] = []
    summary: str
    confidence: float = 0.0

class Event(BaseModel):
    """Complete event with article reference"""
    id: str  # Generated UUID
    article: ArticleContent
    event_data: EventData
    relevance_score: float = 0.0
    
    @property
    def title(self) -> str:
        return self.article.title
    
    @property
    def summary(self) -> str:
        return self.event_data.summary
        
    @property
    def event_type(self) -> str:
        return self.event_data.event_type.value
        
    @property
    def location_full(self) -> str:
        return self.event_data.location.full_text

class SearchQuery(BaseModel):
    """User search query"""
    phrase: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    location: Optional[str] = None
    event_type: Optional[EventType] = None
    sort_by: str = "relevance"  # relevance, date

class SourceConfig(BaseModel):
    """Source configuration"""
    id: int
    name: str
    base_url: str
    enabled: bool = True
    category: Optional[str] = None
    rate_limit_seconds: int = 2
    selectors: Optional[Dict[str, str]] = None  # CSS selectors
    
class SearchResponse(BaseModel):
    """API response for search"""
    query: SearchQuery
    total_results: int
    events: List[Event]
    processing_time_seconds: float
```

---

## 6. API Design

### 6.1 REST API Endpoints

```python
# No authentication required

# Search & Query
POST   /api/v1/search              # Search for events
GET    /api/v1/events/{event_id}   # Get single event details

# Export
POST   /api/v1/export/excel        # Export selected events to Excel

# Configuration (Read-only)
GET    /api/v1/sources              # List configured sources
GET    /api/v1/sources/{id}         # Get source details

# Health Check
GET    /api/v1/health               # API health status
GET    /api/v1/ollama/status        # Ollama connection status
```

### 6.2 API Implementation (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
from io import BytesIO

app = FastAPI(title="Event Scraper API", version="1.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (session-based)
session_store = {}

# Initialize services
config_manager = ConfigManager()
ollama_client = OllamaClient()
scraper = ScraperManager()
entity_extractor = EntityExtractor()
event_extractor = EventExtractor(ollama_client)
query_matcher = QueryMatcher()
excel_exporter = ExcelExporter()

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_events(query: SearchQuery):
    """
    Main search endpoint - triggers scraping and processing
    """
    start_time = time.time()
    session_id = str(uuid.uuid4())
    
    try:
        # 1. Load sources
        sources = config_manager.get_enabled_sources()
        
        # 2. Scrape articles
        articles = await scraper.scrape_sources(sources)
        
        # 3. Extract events
        events = []
        for article in articles:
            # Extract entities with spaCy
            entities = entity_extractor.extract_entities(article.content)
            
            # Extract structured event data with Ollama
            event_data = event_extractor.extract_event_data(article, entities)
            
            # Create event object
            event = Event(
                id=str(uuid.uuid4()),
                article=article,
                event_data=event_data
            )
            events.append(event)
        
        # 4. Filter and rank by relevance
        matched_events = query_matcher.match_events(events, query)
        
        # 5. Store in session
        session_store[session_id] = {
            'query': query,
            'events': matched_events,
            'timestamp': datetime.now()
        }
        
        processing_time = time.time() - start_time
        
        return SearchResponse(
            query=query,
            total_results=len(matched_events),
            events=matched_events,
            processing_time_seconds=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/export/excel")
async def export_excel(event_ids: List[str]):
    """
    Export selected events to Excel
    """
    try:
        # Find events across all sessions (simple approach)
        selected_events = []
        for session_data in session_store.values():
            for event in session_data['events']:
                if event.id in event_ids:
                    selected_events.append(event)
        
        if not selected_events:
            raise HTTPException(status_code=404, detail="No events found")
        
        # Generate Excel
        excel_bytes = excel_exporter.export_events(selected_events)
        
        # Return as downloadable file
        return StreamingResponse(
            BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sources")
async def list_sources():
    """List configured sources"""
    sources = config_manager.load_sources()
    return {"sources": sources}

@app.get("/api/v1/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/ollama/status")
async def ollama_status():
    """Check Ollama connection"""
    try:
        # Test connection
        response = ollama_client.generate("Test", model=ollama_client.default_model)
        return {
            "status": "connected",
            "model": ollama_client.default_model,
            "base_url": ollama_client.base_url
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e)
        }
```

---

## 7. File Storage Strategy

### 7.1 Configuration Files

```
config/
├── sources.yaml              # Source configurations
└── app_config.yaml          # Application settings
```

### 7.2 Generated Excel Files

**Storage Location:** Downloads folder (client-side)

**Naming Convention:** `events_YYYYMMDD_HHMMSS.xlsx`

**Content Structure:**
- Single worksheet named "Events"
- Headers with formatting
- One row per event
- All fields populated

### 7.3 Logs

```
logs/
├── app.log                   # Application logs
├── scraper.log              # Scraping activity
└── ollama.log               # LLM interactions
```

---

## 8. Deployment Architecture

### 8.1 Local Development Setup

**Architecture:**
```
┌─────────────────────────────────────────────┐
│  Development Machine (Windows/Linux/Mac)    │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │  Ollama (Native Installation)      │    │
│  │  - Running on localhost:11434      │    │
│  │  - Model: llama3.1:8b              │    │
│  └────────────────────────────────────┘    │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │  FastAPI Backend (Python)          │    │
│  │  - Running on localhost:8000       │    │
│  │  - Virtual environment             │    │
│  └────────────────────────────────────┘    │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │  React Frontend (Node.js)          │    │
│  │  - Running on localhost:3000       │    │
│  │  - Development server              │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

**Installation Steps:**

1. **Install Ollama** (native)
   - Windows: Download from https://ollama.ai/download/windows
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Mac: Download from https://ollama.ai/download/mac

2. **Pull LLM Model** (if not already installed)
   ```bash
   # Check existing models
   ollama list
   
   # Pull recommended model (if needed)
   ollama pull llama3.1:8b
   
   # Or use your existing model (e.g., gpt-oss:20b)
   # Just configure it in .env file
   ```

3. **Python Backend Setup**
   - Python 3.10+ required
   - Create virtual environment
   - Install dependencies

4. **Frontend Setup**
   - Node.js 18+ required
   - Install npm packages
   - Run development server

### 8.2 Directory Structure

```
event-scraper/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── models.py               # Pydantic models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── scraper.py         # ScraperManager
│   │   │   ├── extractor.py       # ContentExtractor
│   │   │   ├── nlp_service.py     # EntityExtractor
│   │   │   ├── ollama_service.py  # OllamaClient, EventExtractor
│   │   │   ├── query_matcher.py   # QueryMatcher
│   │   │   └── excel_exporter.py  # ExcelExporter
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── rate_limiter.py
│   │   │   ├── config_manager.py
│   │   │   └── logger.py
│   ├── tests/
│   │   ├── test_scraper.py
│   │   ├── test_extractor.py
│   │   └── test_ollama.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchForm.tsx
│   │   │   ├── EventList.tsx
│   │   │   ├── EventCard.tsx
│   │   │   └── ExportButton.tsx
│   │   ├── pages/
│   │   │   └── SearchPage.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
├── config/
│   ├── sources.yaml
│   └── app_config.yaml
├── logs/                      # Created at runtime
├── .env.example
├── .gitignore
├── README.md
└── doc/
    ├── WebScraperRequirementDocument.md
    ├── ArchitectureAndDesignDocument.md
    └── SimplifiedArchitectureDesign.md
```

### 8.3 Configuration Files

#### sources.yaml
```yaml
sources:
  - id: 1
    name: "Example News"
    base_url: "https://example.com/news/latest"
    enabled: true
    category: "General News"
    rate_limit_seconds: 2
    selectors:
      title: "h1.article-title"
      content: "div.article-body"
      date: "time.publish-date"
      
  - id: 2
    name: "Security Blog"
    base_url: "https://security.example.com/blog"
    enabled: true
    category: "Cybersecurity"
    rate_limit_seconds: 3
    selectors: null  # Use generic extraction
```

#### .env
```bash
# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss:20b  # Or llama3.1:8b, mistral:7b, phi3:mini

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Scraping Configuration
DEFAULT_RATE_LIMIT_SECONDS=2
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
USER_AGENT=EventScraperBot/1.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

---

## 9. Development Guidelines

### 9.1 Setup Instructions

**Prerequisites:**
- Python 3.10 or higher
- Node.js 18 or higher
- Git
- Ollama (installed natively)

**Step-by-Step Setup:**

```bash
# 1. Install Ollama (if not already installed)
# Windows: Download installer from https://ollama.ai/download/windows
# Linux: curl -fsSL https://ollama.ai/install.sh | sh
# Mac: Download from https://ollama.ai/download/mac

# 2. Check installed models and pull if needed
ollama list

# If you don't have a model, pull one:
# ollama pull llama3.1:8b
# Or use your existing model (e.g., gpt-oss:20b)

# 3. Verify Ollama is running
# Ollama should auto-start, verify at http://localhost:11434

# 4. Clone repository
git clone <repo-url>
cd event-scraper

# 5. Set up Python backend
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# 6. Download spaCy model
python -m spacy download en_core_web_sm

# 7. Configure sources
cd ..
mkdir -p config
# Create sources.yaml with your target URLs
# (See configuration examples below)

# 8. Create .env file (configure your model)
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
# Edit .env and set OLLAMA_MODEL=gpt-oss:20b (or your preferred model)

# 9. Run backend (in backend directory with venv activated)
cd backend
uvicorn app.main:app --reload --port 8000

# 10. In a new terminal, set up frontend
cd frontend
npm install

# 11. Run frontend development server
npm start

# Application will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 9.2 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

---

## 10. Implementation Phases

### Phase 1: Core Backend (Week 1)
✅ Project structure setup  
✅ FastAPI application skeleton  
✅ Pydantic models  
✅ Configuration manager  
✅ Ollama client integration  

### Phase 2: Scraping (Week 2)
✅ Web scraper implementation  
✅ Content extractor (generic)  
✅ Rate limiter  
✅ Test with sample URLs  

### Phase 3: NLP & Extraction (Week 3)
✅ spaCy entity extraction  
✅ Ollama event extraction  
✅ Event data structuring  
✅ Prompt engineering and testing  

### Phase 4: Query & Matching (Week 4)
✅ Query matcher implementation  
✅ Relevance scoring  
✅ Search API endpoint  
✅ Testing with various queries  

### Phase 5: Excel Export (Week 5)
✅ Excel exporter implementation  
✅ Formatting and styling  
✅ Export API endpoint  
✅ Download handling  

### Phase 6: Frontend (Weeks 6-7)
✅ React app setup  
✅ Search form component  
✅ Event list and cards  
✅ Export functionality  
✅ API integration  

### Phase 7: Testing & Polish (Week 8)
✅ End-to-end testing  
✅ Bug fixes  
✅ Performance optimization  
✅ Documentation  
✅ Deployment guide  

---

## 11. Benefits of Simplified Architecture

### 11.1 Advantages

✅ **Faster Development:** No database schema design or migrations  
✅ **Easier Deployment:** Fewer services to configure  
✅ **Lower Resource Usage:** No database server running  
✅ **Simpler Debugging:** Less moving parts  
✅ **No Data Persistence Issues:** Each session is independent  
✅ **Easy to Understand:** Straightforward data flow  

### 11.2 Limitations

⚠️ **No Historical Data:** Results not saved between sessions  
⚠️ **No User Management:** Single-user focus  
⚠️ **Memory Constraints:** Large result sets may be limited  
⚠️ **No Incremental Scraping:** Scrapes all sources every time  
⚠️ **No Scheduling:** Manual trigger only  

### 11.3 When to Upgrade

Consider adding database when:
- Need to track historical searches
- Want to avoid re-scraping same content
- Multiple concurrent users required
- Need scheduled/automated scraping
- Want to analyze trends over time

---

## 12. Performance Optimization

### 12.1 Caching Strategies

```python
from functools import lru_cache

# Cache scraped content (in-memory)
article_cache = {}

def get_cached_article(url: str) -> Optional[ArticleContent]:
    """Check if article was recently scraped"""
    if url in article_cache:
        cached = article_cache[url]
        # Return if cached less than 1 hour ago
        if (datetime.now() - cached['timestamp']).seconds < 3600:
            return cached['article']
    return None
```

### 12.2 Async Processing

```python
import asyncio

async def process_articles_parallel(articles: List[ArticleContent]) -> List[Event]:
    """Process multiple articles in parallel"""
    tasks = [process_single_article(article) for article in articles]
    events = await asyncio.gather(*tasks)
    return events
```

---

## Appendix A: Example Usage Flow

### User Story: Finding Recent Protests

```
1. User opens web app
2. User enters: "protest in India last week"
3. User clicks "Search"
4. Backend:
   - Loads configured news sources
   - Scrapes latest articles from each source
   - Extracts entities with spaCy
   - Uses Ollama to extract event data
   - Matches events to query
   - Returns ranked results
5. Frontend displays results (e.g., 15 events)
6. User reviews events
7. User selects 8 relevant events
8. User clicks "Export to Excel"
9. Excel file downloads
10. User opens Excel, reviews data
11. Session ends (data not persisted)
```

---

## Appendix B: Error Handling

### Graceful Degradation

```python
def extract_event_with_fallback(article: ArticleContent) -> EventData:
    """Extract event data with fallback to basic extraction"""
    try:
        # Try Ollama extraction
        return ollama_extractor.extract(article)
    except Exception as e:
        logger.warning(f"Ollama extraction failed: {e}, using fallback")
        # Fallback to spaCy-only extraction
        entities = entity_extractor.extract_entities(article.content)
        return create_basic_event_data(article, entities)
```

---

**End of Document**
