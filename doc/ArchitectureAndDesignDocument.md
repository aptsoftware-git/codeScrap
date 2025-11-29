# Architecture and Design Document

## Event-Focused Web Scraping, Summarization & Export Tool

---

## Document Information

**Version:** 1.0  
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
7. [Database Schema](#7-database-schema)
8. [Security Architecture](#8-security-architecture)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Development Guidelines](#10-development-guidelines)
11. [Testing Strategy](#11-testing-strategy)
12. [Performance Considerations](#12-performance-considerations)

---

## 1. Executive Summary

This document outlines the architecture and design for an event-focused web scraping tool that:
- Scrapes content from configurable news sources
- Uses Ollama LLMs for event extraction and summarization
- Provides a web interface for querying and reviewing events
- Exports structured event data to Excel

### 1.1 Key Design Decisions

- **Backend:** Python (FastAPI framework)
- **LLM Engine:** Ollama with local models (llama3, mistral, or phi)
- **Frontend:** React with TypeScript
- **Database:** PostgreSQL for persistence
- **Task Queue:** Celery with Redis for asynchronous scraping
- **Deployment:** Docker containers with docker-compose

---

## 2. Technology Stack

### 2.1 Backend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI | REST API, async support, automatic OpenAPI docs |
| Task Queue | Celery | Asynchronous scraping jobs |
| Message Broker | Redis | Celery backend, caching |
| Database | PostgreSQL | Persistent storage for articles, events |
| ORM | SQLAlchemy | Database abstraction layer |
| Web Scraping | BeautifulSoup4, Playwright | HTML parsing, JS-heavy sites |
| HTTP Client | httpx | Async HTTP requests |
| NLP/NER | spaCy | Named entity recognition |
| LLM Integration | Ollama Python SDK | Local LLM for summarization & extraction |
| Excel Export | openpyxl | Generate .xlsx files |
| Configuration | pydantic-settings | Type-safe configuration |
| Validation | pydantic | Data validation |

### 2.2 Frontend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 18 | UI component library |
| Language | TypeScript | Type safety |
| UI Library | Material-UI (MUI) | Pre-built components |
| State Management | React Query + Zustand | Server state & local state |
| HTTP Client | Axios | API communication |
| Date Handling | date-fns | Date manipulation |
| Routing | React Router | Client-side routing |

### 2.3 DevOps & Infrastructure

- **Containerization:** Docker, Docker Compose
- **Process Manager:** Supervisor (for Celery workers)
- **Logging:** Python logging + Loguru
- **Monitoring:** Prometheus + Grafana (optional)
- **Testing:** pytest, React Testing Library

### 2.4 Ollama Configuration

**Recommended Models:**
- **Primary:** `llama3.1:8b` or `mistral:7b` - Good balance of performance and accuracy
- **Lightweight:** `phi3:mini` - Faster inference for high-volume processing
- **Specialized:** `llama3.1:70b` - Higher accuracy for complex event extraction (if hardware allows)

**Model Selection Strategy:**
- Use lightweight models for initial filtering and classification
- Use larger models for detailed summarization and entity extraction
- Implement model switching based on task complexity

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           React Frontend (Web Browser)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTPS/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   FastAPI Application                     │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │   Auth     │  │   Query      │  │    Export       │  │  │
│  │  │   API      │  │   API        │  │    API          │  │  │
│  │  └────────────┘  └──────────────┘  └─────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BUSINESS LOGIC LAYER                      │
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
│                    ASYNCHRONOUS TASK LAYER                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Celery Workers (with Redis)                 │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │  Scraping  │  │  Processing  │  │   Batch Jobs    │  │  │
│  │  │   Tasks    │  │   Tasks      │  │                 │  │  │
│  │  └────────────┘  └──────────────┘  └─────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Ollama LLM  │  │  PostgreSQL  │  │      Redis           │ │
│  │   Server     │  │   Database   │  │   (Cache/Queue)      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Interaction Flow

#### Scraping Flow
```
1. User initiates search → FastAPI endpoint
2. FastAPI creates Celery task → Task Queue
3. Celery worker picks up task
4. Worker fetches configured URLs → Web Scraper
5. Web Scraper extracts content → NLP Service
6. NLP Service extracts entities → Ollama LLM
7. Ollama generates summaries and extracts structured data
8. Results stored in PostgreSQL
9. User notified via WebSocket/polling
```

#### Query Flow
```
1. User submits query → Query API
2. Query API builds filters → Database query
3. PostgreSQL returns matching events
4. Results ranked by relevance
5. Response sent to frontend
```

#### Export Flow
```
1. User selects events → Export API
2. Export API retrieves full event data
3. Excel Service generates .xlsx file
4. File served as download
```

---

## 4. Component Design

### 4.1 Web Scraper Service

**Responsibility:** Fetch and parse content from configured URLs

**Modules:**

#### 4.1.1 ScraperManager
```python
class ScraperManager:
    """Orchestrates scraping across multiple sources"""
    
    def scrape_sources(self, source_ids: List[int]) -> List[ScrapedArticle]:
        """Scrape multiple sources with rate limiting"""
        
    def scrape_single_source(self, source: Source) -> List[ScrapedArticle]:
        """Scrape a single source"""
        
    def respect_robots_txt(self, domain: str) -> bool:
        """Check robots.txt compliance"""
```

#### 4.1.2 ContentExtractor
```python
class ContentExtractor:
    """Extract structured content from HTML"""
    
    def extract_generic(self, html: str, url: str) -> ArticleContent:
        """Generic extraction using newspaper3k or trafilatura"""
        
    def extract_with_selector(self, html: str, selectors: dict) -> ArticleContent:
        """Site-specific extraction using CSS selectors"""
        
    def clean_content(self, text: str) -> str:
        """Remove boilerplate, ads, navigation"""
```

#### 4.1.3 RateLimiter
```python
class RateLimiter:
    """Enforce rate limits per domain"""
    
    def can_request(self, domain: str) -> bool:
        """Check if request is allowed"""
        
    def record_request(self, domain: str) -> None:
        """Record request timestamp"""
```

### 4.2 NLP Service

**Responsibility:** Named entity recognition and text preprocessing

**Modules:**

#### 4.2.1 EntityExtractor
```python
class EntityExtractor:
    """Extract named entities using spaCy"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        
    def extract_entities(self, text: str) -> ExtractedEntities:
        """Extract persons, organizations, locations, dates"""
        
    def extract_locations(self, text: str) -> List[Location]:
        """Extract and geocode locations"""
        
    def extract_dates(self, text: str) -> List[DateRange]:
        """Extract temporal expressions"""
```

### 4.3 Event Extraction Service (Ollama Integration)

**Responsibility:** Use LLM to identify, classify, and extract event information

**Modules:**

#### 4.3.1 OllamaClient
```python
class OllamaClient:
    """Wrapper for Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.client = ollama.Client(base_url)
        
    def generate(self, prompt: str, model: str = "llama3.1:8b") -> str:
        """Generate completion"""
        
    def generate_structured(self, prompt: str, schema: dict, model: str) -> dict:
        """Generate structured JSON output"""
```

#### 4.3.2 EventClassifier
```python
class EventClassifier:
    """Classify event types using Ollama"""
    
    def classify_event_type(self, text: str) -> EventType:
        """Classify: protest, attack, accident, etc."""
        
    def extract_perpetrator(self, text: str, event_type: str) -> Optional[str]:
        """Extract perpetrator if applicable"""
```

#### 4.3.3 EventSummarizer
```python
class EventSummarizer:
    """Generate event summaries using Ollama"""
    
    def summarize_event(self, article: Article, entities: ExtractedEntities) -> Summary:
        """Generate concise 2-4 sentence summary"""
        
    def generate_title(self, summary: str) -> str:
        """Generate descriptive title (max 120 chars)"""
```

#### 4.3.4 StructuredExtractor
```python
class StructuredExtractor:
    """Extract structured fields from events"""
    
    def extract_all_fields(self, article: Article) -> EventData:
        """
        Extract all structured fields:
        - Event type
        - Perpetrator
        - Location (city, region, country)
        - Time (date, time of day)
        - Individuals involved
        - Organizations involved
        """
        
    def build_extraction_prompt(self, text: str, entities: dict) -> str:
        """Build optimized prompt for field extraction"""
```

**Prompt Engineering Strategy:**

```python
# Example prompt for structured extraction
EXTRACTION_PROMPT = """
You are an expert analyst extracting structured information from news articles.

Article: {article_text}

Extract the following information about the main event described:

1. Event Type: Choose from [protest, attack, bombing, cyber_attack, accident, 
   natural_disaster, conference, meeting, arrest, theft, other]

2. Perpetrator: Individual, group, or organization responsible (if applicable).
   If unknown or not applicable, write "Unknown".

3. Location: Extract hierarchical location:
   - City: 
   - Region/State:
   - Country:

4. Time:
   - Date: (YYYY-MM-DD format)
   - Time of day: (HH:MM if mentioned, else "Not specified")

5. Individuals: List all named people mentioned (comma-separated)

6. Organizations: List all organizations mentioned (comma-separated)

7. Brief Description: One sentence summary of what happened.

Respond in valid JSON format:
{{
  "event_type": "",
  "perpetrator": "",
  "location": {{"city": "", "region": "", "country": ""}},
  "date": "",
  "time": "",
  "individuals": [],
  "organizations": [],
  "description": "",
  "confidence": 0.0-1.0
}}
"""
```

### 4.4 Query Matching Service

**Responsibility:** Match events against user queries and filters

**Modules:**

#### 4.4.1 QueryParser
```python
class QueryParser:
    """Parse natural language queries"""
    
    def parse_query(self, query_text: str) -> ParsedQuery:
        """Extract intent, entities, constraints from query"""
        
    def extract_temporal_constraints(self, query: str) -> Optional[DateRange]:
        """Extract time references"""
        
    def extract_location_constraints(self, query: str) -> Optional[Location]:
        """Extract location references"""
```

#### 4.4.2 RelevanceScorer
```python
class RelevanceScorer:
    """Score event relevance to query"""
    
    def score_event(self, event: Event, query: ParsedQuery) -> float:
        """
        Calculate relevance score based on:
        - Keyword match (TF-IDF, BM25)
        - Location match
        - Temporal match
        - Event type match
        """
        
    def rank_events(self, events: List[Event], query: ParsedQuery) -> List[Event]:
        """Sort events by relevance score"""
```

### 4.5 Export Service

**Responsibility:** Generate Excel files from selected events

**Modules:**

#### 4.5.1 ExcelGenerator
```python
class ExcelGenerator:
    """Generate Excel files using openpyxl"""
    
    def generate_event_export(self, events: List[Event]) -> bytes:
        """
        Generate .xlsx with columns:
        - Event Title
        - Summary
        - Event Type
        - Perpetrator
        - Location (full)
        - City, Region, Country
        - Event Date, Event Time
        - Individuals Involved
        - Organizations Involved
        - Source Name, Source URL
        - Publication Date
        - Confidence Score
        """
        
    def apply_formatting(self, worksheet) -> None:
        """Apply styling, filters, column widths"""
```

### 4.6 Configuration Manager

**Responsibility:** Manage source configurations and scraping rules

**Modules:**

#### 4.6.1 SourceConfig
```python
class SourceConfig(BaseModel):
    """Configuration for a scraping source"""
    id: int
    name: str
    base_url: str
    enabled: bool
    category: str
    rate_limit_seconds: int
    selectors: Optional[Dict[str, str]]  # CSS selectors
    custom_parser: Optional[str]  # Python module path
```

---

## 5. Data Models

### 5.1 Core Models (Pydantic)

```python
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum

class EventType(str, Enum):
    PROTEST = "protest"
    ATTACK = "attack"
    BOMBING = "bombing"
    CYBER_ATTACK = "cyber_attack"
    ACCIDENT = "accident"
    NATURAL_DISASTER = "natural_disaster"
    CONFERENCE = "conference"
    ARREST = "arrest"
    THEFT = "theft"
    OTHER = "other"

class Location(BaseModel):
    city: Optional[str]
    region: Optional[str]
    country: Optional[str]
    full_text: str
    latitude: Optional[float]
    longitude: Optional[float]

class ExtractedEntities(BaseModel):
    persons: List[str]
    organizations: List[str]
    locations: List[Location]
    dates: List[str]

class EventData(BaseModel):
    event_type: EventType
    perpetrator: Optional[str]
    location: Location
    event_date: Optional[datetime]
    event_time: Optional[str]
    individuals: List[str]
    organizations: List[str]
    description: str
    confidence: float

class Article(BaseModel):
    url: HttpUrl
    title: str
    content: str
    publication_date: Optional[datetime]
    source_name: str
    scraped_at: datetime
    
class Event(BaseModel):
    id: int
    article_id: int
    title: str
    summary: str
    event_data: EventData
    relevance_score: Optional[float]
    created_at: datetime

class SearchQuery(BaseModel):
    phrase: str
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    location: Optional[str]
    event_type: Optional[EventType]
    sort_by: str = "relevance"  # relevance, date, publication_date
    page: int = 1
    page_size: int = 50
```

---

## 6. API Design

### 6.1 REST API Endpoints

#### Authentication
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
```

#### Sources
```
GET    /api/v1/sources
GET    /api/v1/sources/{id}
POST   /api/v1/sources
PUT    /api/v1/sources/{id}
DELETE /api/v1/sources/{id}
PATCH  /api/v1/sources/{id}/enable
PATCH  /api/v1/sources/{id}/disable
```

#### Scraping
```
POST   /api/v1/scrape/trigger          # Trigger scraping job
GET    /api/v1/scrape/status/{job_id}  # Get job status
GET    /api/v1/scrape/jobs              # List recent jobs
```

#### Search & Query
```
POST   /api/v1/search                   # Search for events
GET    /api/v1/events/{id}              # Get event details
GET    /api/v1/events                   # List all events (paginated)
```

#### Export
```
POST   /api/v1/export/excel             # Export selected events
       Body: { "event_ids": [1, 2, 3] }
       Response: Excel file download
```

### 6.2 API Request/Response Examples

#### Search Request
```json
POST /api/v1/search
{
  "phrase": "protest near refinery in Gujarat",
  "date_from": "2025-03-01",
  "date_to": "2025-03-31",
  "location": "Gujarat",
  "event_type": null,
  "sort_by": "relevance",
  "page": 1,
  "page_size": 20
}
```

#### Search Response
```json
{
  "total": 15,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 123,
      "title": "Workers Protest at Jamnagar Refinery Over Safety Concerns",
      "summary": "Over 500 workers gathered outside the Jamnagar refinery on March 12 to protest unsafe working conditions. The demonstration remained peaceful with demands for improved safety measures. Local authorities monitored the situation.",
      "event_data": {
        "event_type": "protest",
        "perpetrator": null,
        "location": {
          "city": "Jamnagar",
          "region": "Gujarat",
          "country": "India",
          "full_text": "Jamnagar, Gujarat, India"
        },
        "event_date": "2025-03-12T00:00:00Z",
        "event_time": "10:00",
        "individuals": ["Union Leader Ramesh Kumar"],
        "organizations": ["Workers Union of Gujarat", "Jamnagar Refinery"],
        "description": "Workers protest over safety concerns",
        "confidence": 0.87
      },
      "source_name": "Gujarat News Daily",
      "source_url": "https://example.com/article/123",
      "publication_date": "2025-03-12T15:30:00Z",
      "relevance_score": 0.92
    }
  ]
}
```

---

## 7. Database Schema

### 7.1 PostgreSQL Tables

```sql
-- Sources configuration
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    base_url TEXT NOT NULL,
    enabled BOOLEAN DEFAULT true,
    category VARCHAR(100),
    rate_limit_seconds INTEGER DEFAULT 2,
    selectors JSONB,
    custom_parser VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Scraped articles
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    url TEXT UNIQUE NOT NULL,
    url_hash VARCHAR(64) NOT NULL,  -- SHA256 for deduplication
    title TEXT,
    content TEXT,
    publication_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_url_hash (url_hash),
    INDEX idx_publication_date (publication_date)
);

-- Extracted events
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    title VARCHAR(255),
    summary TEXT,
    event_type VARCHAR(50),
    perpetrator TEXT,
    
    -- Location fields
    location_full TEXT,
    location_city VARCHAR(100),
    location_region VARCHAR(100),
    location_country VARCHAR(100),
    location_lat DECIMAL(10, 8),
    location_lon DECIMAL(11, 8),
    
    -- Temporal fields
    event_date DATE,
    event_time TIME,
    
    -- Entities
    individuals TEXT[],
    organizations TEXT[],
    
    -- Metadata
    confidence DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_event_type (event_type),
    INDEX idx_event_date (event_date),
    INDEX idx_location_country (location_country)
);

-- Full-text search
CREATE INDEX idx_events_summary_fts ON events 
    USING gin(to_tsvector('english', summary));

CREATE INDEX idx_articles_content_fts ON articles 
    USING gin(to_tsvector('english', content));

-- Scraping jobs
CREATE TABLE scraping_jobs (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20),  -- pending, running, completed, failed
    sources INTEGER[],
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    articles_scraped INTEGER DEFAULT 0,
    events_extracted INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User queries (for analytics)
CREATE TABLE query_log (
    id SERIAL PRIMARY KEY,
    query_phrase TEXT,
    filters JSONB,
    results_count INTEGER,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 8. Security Architecture

### 8.1 Authentication & Authorization

**v1 Implementation:**
- Basic HTTP authentication for admin endpoints
- API key for programmatic access
- Session-based auth for web UI

**Future Enhancement:**
- OAuth2 with JWT tokens
- Role-based access control (RBAC)
- User management

### 8.2 Data Security

- **Secrets Management:** Environment variables, never in code
- **Database:** Encrypted connections (SSL/TLS)
- **API:** HTTPS only in production
- **Input Validation:** Pydantic models for all inputs
- **SQL Injection:** SQLAlchemy ORM prevents SQL injection

### 8.3 Rate Limiting

- API rate limiting: 100 requests/minute per IP
- Scraping rate limiting: Configurable per domain
- Respect robots.txt

---

## 9. Deployment Architecture

### 9.1 Docker Compose Setup

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: event_scraper
      POSTGRES_USER: scraper_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis for Celery
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Ollama LLM Server
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]  # Optional: for GPU acceleration

  # FastAPI Backend
  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://scraper_user:${DB_PASSWORD}@postgres/event_scraper
      REDIS_URL: redis://redis:6379/0
      OLLAMA_URL: http://ollama:11434
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
      - redis
      - ollama
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app

  # Celery Worker
  celery_worker:
    build: ./backend
    command: celery -A app.tasks worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://scraper_user:${DB_PASSWORD}@postgres/event_scraper
      REDIS_URL: redis://redis:6379/0
      OLLAMA_URL: http://ollama:11434
    depends_on:
      - postgres
      - redis
      - ollama
    volumes:
      - ./backend:/app

  # React Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - api

volumes:
  postgres_data:
  ollama_data:
```

### 9.2 Directory Structure

```
event-scraper/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # Database setup
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── source.py
│   │   │   ├── article.py
│   │   │   └── event.py
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── event.py
│   │   │   └── query.py
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   ├── sources.py
│   │   │   ├── search.py
│   │   │   └── export.py
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── scraper.py
│   │   │   ├── extractor.py
│   │   │   ├── nlp_service.py
│   │   │   ├── ollama_service.py
│   │   │   ├── query_service.py
│   │   │   └── export_service.py
│   │   ├── tasks/                  # Celery tasks
│   │   │   ├── __init__.py
│   │   │   └── scraping.py
│   │   └── utils/                  # Utilities
│   │       ├── __init__.py
│   │       ├── rate_limiter.py
│   │       └── prompts.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/                    # Database migrations
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchForm.tsx
│   │   │   ├── EventList.tsx
│   │   │   ├── EventCard.tsx
│   │   │   └── ExportButton.tsx
│   │   ├── pages/
│   │   │   ├── SearchPage.tsx
│   │   │   ├── ResultsPage.tsx
│   │   │   └── SourcesPage.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── doc/
    ├── WebScraperRequirementDocument.md
    └── ArchitectureAndDesignDocument.md
```

---

## 10. Development Guidelines

### 10.1 Code Standards

**Python:**
- Follow PEP 8
- Type hints for all functions
- Docstrings (Google style)
- Max line length: 100 characters
- Use Black for formatting
- Use pylint/flake8 for linting

**TypeScript:**
- ESLint + Prettier
- Functional components with hooks
- Strict type checking
- Meaningful variable names

### 10.2 Git Workflow

- Feature branches: `feature/feature-name`
- Bugfix branches: `bugfix/bug-name`
- Main branch: protected, requires PR review
- Commit messages: Conventional Commits format

### 10.3 Testing Requirements

- Unit test coverage: >80%
- Integration tests for API endpoints
- E2E tests for critical user flows
- Mock Ollama responses in tests

---

## 11. Testing Strategy

### 11.1 Backend Testing

```python
# Unit Tests
tests/
├── test_scraper.py          # Test scraping logic with mock HTML
├── test_nlp_service.py      # Test entity extraction
├── test_ollama_service.py   # Test with mock Ollama responses
├── test_query_service.py    # Test relevance scoring
└── test_export_service.py   # Test Excel generation

# Integration Tests
tests/integration/
├── test_api_endpoints.py    # Test all API endpoints
├── test_celery_tasks.py     # Test async tasks
└── test_database.py         # Test database operations
```

### 11.2 Frontend Testing

```typescript
// Component Tests
src/components/__tests__/
├── SearchForm.test.tsx
├── EventList.test.tsx
└── EventCard.test.tsx

// Integration Tests
src/__tests__/
├── SearchFlow.test.tsx      # Test full search flow
└── ExportFlow.test.tsx      # Test export flow
```

### 11.3 Test Data

- Sample HTML pages from various news sites
- Mock Ollama responses for different event types
- Seed database with sample events
- Test queries with known expected results

---

## 12. Performance Considerations

### 12.1 Optimization Strategies

**Scraping:**
- Parallel scraping with connection pooling
- Caching of robots.txt
- Resume capability for interrupted jobs
- Incremental scraping (only new articles)

**LLM Processing:**
- Batch processing where possible
- Model selection based on task complexity
- Caching of repeated extractions
- Queue prioritization (user queries > batch jobs)

**Database:**
- Indexes on frequently queried fields
- Full-text search indexes
- Connection pooling
- Query result caching (Redis)

**API:**
- Response caching for common queries
- Pagination for large result sets
- Async endpoints for long-running operations
- WebSocket for real-time job status

### 12.2 Scalability

**Horizontal Scaling:**
- Stateless API servers (can scale horizontally)
- Multiple Celery workers
- Load balancer for API

**Vertical Scaling:**
- Ollama with GPU for faster inference
- Larger models for better accuracy

### 12.3 Monitoring & Logging

**Metrics to Track:**
- Scraping success rate
- Average LLM inference time
- API response times
- Database query performance
- Celery queue length

**Logging:**
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized logging (optional: ELK stack)

---

## 13. Ollama-Specific Implementation Details

### 13.1 Model Management

```python
class OllamaModelManager:
    """Manage Ollama models and selection"""
    
    MODELS = {
        "fast": "phi3:mini",           # Quick classification
        "balanced": "llama3.1:8b",     # General purpose
        "accurate": "llama3.1:70b"     # High accuracy (if hardware allows)
    }
    
    def select_model_for_task(self, task_type: str) -> str:
        """Select appropriate model based on task"""
        model_map = {
            "classification": "fast",
            "extraction": "balanced",
            "summarization": "balanced",
            "complex_extraction": "accurate"
        }
        return self.MODELS[model_map.get(task_type, "balanced")]
```

### 13.2 Prompt Templates

```python
# Located in app/utils/prompts.py

EVENT_CLASSIFICATION_PROMPT = """
Classify the following news text into ONE event type.

Text: {text}

Event types: protest, attack, bombing, cyber_attack, accident, natural_disaster, 
conference, meeting, arrest, theft, other

Respond with just the event type in lowercase.
"""

SUMMARIZATION_PROMPT = """
Summarize the following news article in 2-4 sentences. Focus on:
1. What happened (the main event)
2. Where it happened
3. When it happened
4. Who was involved

Article: {article_text}

Summary:
"""

STRUCTURED_EXTRACTION_PROMPT = """
[See Section 4.3.4 for full prompt]
"""
```

### 13.3 Error Handling for Ollama

```python
class OllamaService:
    def __init__(self):
        self.client = ollama.Client()
        self.max_retries = 3
        self.timeout = 60
        
    async def generate_with_retry(self, prompt: str, model: str) -> str:
        """Generate with automatic retry on failure"""
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(
                    self.client.generate(model=model, prompt=prompt),
                    timeout=self.timeout
                )
                return response['response']
            except asyncio.TimeoutError:
                logger.warning(f"Ollama timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

---

## 14. Implementation Phases

### Phase 1: Core Infrastructure (Weeks 1-2)
- ✓ Set up project structure
- ✓ Docker compose configuration
- ✓ Database schema and migrations
- ✓ Basic FastAPI app with health check
- ✓ Ollama integration and testing

### Phase 2: Scraping Engine (Weeks 3-4)
- ✓ Web scraper implementation
- ✓ Content extraction (generic + custom)
- ✓ Rate limiting
- ✓ Celery task queue setup
- ✓ Source configuration system

### Phase 3: NLP & Event Extraction (Weeks 5-6)
- ✓ spaCy NER integration
- ✓ Ollama prompts for classification
- ✓ Ollama prompts for extraction
- ✓ Event summarization
- ✓ Testing with sample articles

### Phase 4: Query & Search (Week 7)
- ✓ Query parsing
- ✓ Relevance scoring
- ✓ Search API endpoints
- ✓ Database indexing optimization

### Phase 5: Frontend (Weeks 8-9)
- ✓ React app setup
- ✓ Search form component
- ✓ Results list component
- ✓ Event card component
- ✓ API integration

### Phase 6: Export Functionality (Week 10)
- ✓ Excel generation
- ✓ Export API endpoint
- ✓ Frontend export button
- ✓ File download handling

### Phase 7: Testing & Refinement (Weeks 11-12)
- ✓ Unit test suite
- ✓ Integration tests
- ✓ End-to-end testing
- ✓ Performance optimization
- ✓ Bug fixes
- ✓ Documentation

---

## 15. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Ollama inference too slow | High | Medium | Use lighter models, GPU acceleration, batch processing |
| Website structure changes | Medium | High | Pluggable extractors, fallback to generic extraction |
| Rate limiting by sites | Medium | Medium | Respect robots.txt, implement delays, rotate user agents |
| Poor extraction accuracy | High | Medium | Iterative prompt engineering, model fine-tuning |
| Database performance issues | Medium | Low | Proper indexing, query optimization, caching |
| Ollama server downtime | High | Low | Retry logic, graceful degradation, health checks |

---

## 16. Future Enhancements

### Post-v1 Features
1. **User Accounts:** Multi-user support with saved queries
2. **Scheduled Scraping:** Cron-based periodic scraping
3. **Notifications:** Email/webhook alerts for new matching events
4. **Visualization:** Interactive maps and timelines
5. **Multi-language:** Support for non-English sources
6. **Fine-tuned Models:** Custom Ollama models trained on event data
7. **API Documentation:** Interactive OpenAPI/Swagger docs
8. **Admin Dashboard:** Monitor scraping, view statistics
9. **Export Formats:** PDF, CSV, JSON in addition to Excel
10. **Event Editing:** Manual correction of extracted data

---

## 17. References & Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- Ollama: https://ollama.ai/
- spaCy: https://spacy.io/
- Celery: https://docs.celeryproject.org/
- SQLAlchemy: https://www.sqlalchemy.org/
- React: https://react.dev/

### Similar Projects
- NewsPlease: https://github.com/fhamborg/news-please
- GDELT Project: https://www.gdeltproject.org/
- CommonCrawl: https://commoncrawl.org/

---

## Appendix A: Configuration File Examples

### sources.yaml
```yaml
sources:
  - id: 1
    name: "Example News"
    base_url: "https://example.com/news"
    enabled: true
    category: "General News"
    rate_limit_seconds: 2
    selectors:
      title: "h1.article-title"
      content: "div.article-body"
      date: "time.publish-date"
      
  - id: 2
    name: "Cyber Security Blog"
    base_url: "https://cybersec.example.com/blog"
    enabled: true
    category: "Cybersecurity"
    rate_limit_seconds: 3
    custom_parser: "parsers.cybersec_parser"
```

### .env.example
```bash
# Database
DATABASE_URL=postgresql://scraper_user:password@localhost/event_scraper

# Redis
REDIS_URL=redis://localhost:6379/0

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.1:8b

# API
SECRET_KEY=your-secret-key-here
API_RATE_LIMIT=100

# Scraping
DEFAULT_RATE_LIMIT_SECONDS=2
MAX_CONCURRENT_REQUESTS=5
USER_AGENT=EventScraperBot/1.0

# Logging
LOG_LEVEL=INFO
```

---

## Document Control

**Approval:**
- [ ] Technical Lead
- [ ] Product Owner
- [ ] Security Review
- [ ] DevOps Review

**Change Log:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-26 | System Architect | Initial draft |

---

**End of Document**
