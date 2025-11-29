# Incremental Implementation Plan

## Event-Focused Web Scraping Tool - Step-by-Step Guide

**Version:** 1.0  
**Last Updated:** November 2025  
**Related:** SimplifiedArchitectureDesign.md

---

## Overview

This document provides a practical, incremental implementation plan for building the event scraping tool. Each increment delivers working functionality that can be tested independently.

---

## Technology Prerequisites

### Required Software
- Python 3.10+
- Node.js 18+
- Ollama (native installation)
- Git

### Python Packages
```bash
fastapi uvicorn pydantic
httpx beautifulsoup4 lxml
spacy ollama
openpyxl pyyaml
loguru pytest
```

### Frontend Packages
```bash
react react-router-dom
@mui/material @emotion/react
axios date-fns
typescript
```

### Installation Steps
1. **Install Ollama**: Download from https://ollama.ai/download
2. **Check Models**: Run `ollama list` to see installed models
3. **Pull Model (if needed)**: 
   - `ollama pull llama3.1:8b` (recommended for 16GB+ RAM systems) ⭐
   - `ollama pull llama3.2:3b` (good for 8-12GB RAM systems)
   - `ollama pull phi3:mini` (good for 8GB RAM systems)
   - `ollama pull gemma3:1b` (for 4-8GB RAM systems only)
   - Note: Avoid gpt-oss:20b unless you have 16GB+ RAM and need absolute best accuracy
4. **Verify**: Check http://localhost:11434 is accessible

### Model Selection Guide
- **llama3.1:8b**: Excellent accuracy, balanced speed, requires ~8-10 GiB RAM ⭐ **RECOMMENDED for 16GB+ systems**
- **llama3.2:3b**: Good accuracy, faster, requires ~4 GiB RAM (for 8GB systems)
- **phi3:mini**: Balanced speed/accuracy, requires ~4 GiB RAM
- **gemma3:1b**: Fast but lower accuracy, requires ~2 GiB RAM (for 4-8GB systems)
- **gpt-oss:20b**: Best accuracy but very slow, requires 12+ GiB RAM (overkill for most tasks)

---

## Implementation Increments

### **Increment 1: Project Setup & Ollama Integration** (2-3 days)

**Goal:** Basic project structure with working Ollama connection

**Tasks:**
1. Install Ollama natively on development machine
   - Download from https://ollama.ai/download
   - Verify installed models: `ollama list`
   - Pull llama3.1:8b for best balance: `ollama pull llama3.1:8b`
   - **Important:** Choose model based on available RAM:
     - 16GB+ RAM → llama3.1:8b (recommended)
     - 8-12GB RAM → llama3.2:3b
     - 4-8GB RAM → gemma3:1b
   - Verify running on localhost:11434

2. Create directory structure
   ```
   event-scraper/
   ├── backend/app/
   ├── frontend/src/
   ├── config/
   └── .env.example
   ```

3. Set up Python virtual environment
   - Create venv
   - Install FastAPI and dependencies
   - Create requirements.txt

4. Create basic FastAPI app
   - `/api/v1/health` endpoint
   - `/api/v1/ollama/status` endpoint
   - CORS configuration

5. Implement OllamaClient wrapper
   - `generate()` method
   - `generate_json()` method
   - Connection testing
   - Support configurable model via environment variable

**Deliverable:** Working API that can communicate with Ollama

**Test:** 
```bash
# Set your model in .env file
# OLLAMA_MODEL=llama3.1:8b

# In one terminal (backend with venv activated)
uvicorn app.main:app --reload

# In another terminal
curl http://localhost:8000/api/v1/ollama/status
# Should show your configured model (llama3.1:8b)
```

---

### **Increment 2: Configuration & Data Models** (2 days)

**Goal:** Load source configurations and define data structures

**Tasks:**
1. Create Pydantic models in `models.py`
   - EventType, Location, ExtractedEntities
   - ArticleContent, EventData, Event
   - SearchQuery, SourceConfig, SearchResponse

2. Implement ConfigManager
   - Load sources from YAML
   - Validate configurations
   - Get enabled sources

3. Create sample `sources.yaml`
   - 2-3 test news sources
   - Include selectors for each

4. Add `/api/v1/sources` endpoint

**Deliverable:** API returns configured sources from YAML

**Test:**
```bash
curl http://localhost:8000/api/v1/sources
```

---

### **Increment 3: Web Scraping Engine** (3-4 days)

**Goal:** Fetch and extract content from configured URLs

**Tasks:**
1. Implement RateLimiter utility
   - Per-domain rate limiting
   - Configurable delays

2. Create ScraperManager
   - Async URL fetching with httpx
   - Retry logic for failures
   - Respect rate limits

3. Implement ContentExtractor
   - Generic extraction (BeautifulSoup)
   - Selector-based extraction
   - Content cleaning

4. Add logging for scraping activity

**Deliverable:** Can scrape articles from configured sources

**Test:**
```python
# Test script
scraper = ScraperManager()
articles = await scraper.scrape_sources(sources)
print(f"Scraped {len(articles)} articles")
```

---

### **Increment 4: NLP Entity Extraction** (2 days)

**Goal:** Extract named entities using spaCy

**Tasks:**
1. Download spaCy model
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. Implement EntityExtractor
   - Extract persons, organizations, locations, dates
   - Handle entity deduplication

3. Create unit tests
   - Test with sample news text
   - Verify entity extraction accuracy

**Deliverable:** Entity extraction from article text

**Test:**
```python
extractor = EntityExtractor()
entities = extractor.extract_entities(article_text)
assert len(entities.persons) > 0
```

---

### **Increment 5: Event Extraction with Ollama** (4-5 days)

**Goal:** Use LLM to extract structured event data

**Tasks:**
1. Design extraction prompts
   - Event type classification
   - Structured field extraction
   - Summary generation

2. Implement EventExtractor
   - Build comprehensive prompt
   - Parse JSON responses
   - Handle extraction errors

3. Create fallback mechanism
   - Basic extraction if Ollama fails
   - Use spaCy entities as backup

4. Test with various article types
   - Protests, attacks, conferences
   - Verify accuracy and consistency

**Deliverable:** Structured event data from articles

**Test:**
```python
event_data = event_extractor.extract_event_data(article, entities)
assert event_data.event_type in EventType
assert event_data.confidence > 0.5
```

---

### **Increment 6: Query Matching & Relevance** (2-3 days)

**Goal:** Filter and rank events by relevance to user query

**Tasks:**
1. Implement QueryMatcher
   - Text similarity (keyword matching)
   - Location matching
   - Date range filtering
   - Event type filtering

2. Create relevance scoring algorithm
   - Weighted scoring (text, location, date, type)
   - Threshold filtering
   - Sorting by score

3. Test with various queries
   - "protest in Mumbai"
   - "cyber attack last week"
   - "bombing in Middle East"

**Deliverable:** Ranked event results based on query

**Test:**
```python
matched = query_matcher.match_events(events, query)
assert matched[0].relevance_score >= matched[1].relevance_score
```

---

### **Increment 7: Search API Endpoint** (2 days)

**Goal:** Complete end-to-end search functionality

**Tasks:**
1. Implement `/api/v1/search` endpoint
   - Accept SearchQuery
   - Orchestrate: scrape → extract → match
   - Store results in session

2. Add in-memory session store
   - UUID-based sessions
   - Store query results

3. Add error handling
   - Graceful failures
   - Informative error messages

4. Add timing/metrics
   - Processing time tracking
   - Article count, event count

**Deliverable:** Full search API working end-to-end

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"phrase": "protest in India", "date_from": "2025-01-01"}'
```

---

### **Increment 8: Excel Export Service** (2-3 days)

**Goal:** Export selected events to Excel

**Tasks:**
1. Implement ExcelExporter
   - Create workbook with headers
   - Format cells (colors, alignment)
   - Auto-adjust column widths
   - Write event data

2. Implement `/api/v1/export/excel` endpoint
   - Accept event IDs
   - Generate Excel file
   - Stream file download

3. Test Excel output
   - Verify all columns present
   - Check formatting
   - Open in Excel/LibreOffice

**Deliverable:** Working Excel export

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/export/excel \
  -H "Content-Type: application/json" \
  -d '{"event_ids": ["uuid1", "uuid2"]}' \
  --output events.xlsx
```

---

### **Increment 9: React Frontend - Search Form** (3 days)

**Goal:** UI for entering search queries

**Tasks:**
1. Set up React project with TypeScript
   - Create React App or Vite
   - Install MUI and dependencies

2. Create SearchForm component
   - Text input for phrase
   - Date pickers (from/to)
   - Location input
   - Event type dropdown
   - Submit button

3. Create API service layer
   - Axios client configuration
   - API call functions

4. Wire up form to API
   - Handle form submission
   - Show loading state
   - Display errors

**Deliverable:** Working search form that calls API

---

### **Increment 10: React Frontend - Results Display** (3-4 days)

**Goal:** Display search results with export capability

**Tasks:**
1. Create EventCard component
   - Display title, summary, metadata
   - Checkbox for selection
   - Link to source

2. Create EventList component
   - Render list of EventCards
   - Handle selection state
   - Show result count

3. Create ExportButton component
   - Trigger Excel export
   - Handle file download
   - Show export status

4. Integrate all components
   - Search → Results → Export flow
   - Error handling
   - Loading states

**Deliverable:** Complete frontend application

---

### **Increment 11: Production Readiness** (2 days)

**Goal:** Prepare application for deployment and production use

**Tasks:**
1. Add error handling and validation
   - Input validation
   - Graceful error messages
   - Logging improvements

2. Create comprehensive documentation
   - README.md with setup instructions
   - Configuration guide
   - API documentation

3. Add production configuration
   - Environment variables
   - Production-ready settings
   - Security headers

4. Create deployment guide
   - Installation steps
   - Configuration options
   - Troubleshooting guide

**Deliverable:** Production-ready application with documentation

---

### **Increment 12: Testing & Documentation** (3-4 days)

**Goal:** Comprehensive testing and user documentation

**Tasks:**
1. Write unit tests
   - Test each service independently
   - Mock external dependencies
   - Aim for >70% coverage

2. Write integration tests
   - Test API endpoints
   - Test full workflow

3. Create user documentation
   - Installation guide
   - Configuration guide
   - Usage examples
   - Troubleshooting

4. Create developer documentation
   - Code structure
   - Adding new sources
   - Customizing prompts

**Deliverable:** Tested, documented application ready for use

---

## Total Timeline

**Estimated Duration:** 6-8 weeks (1 developer)

- Weeks 1-2: Increments 1-4 (Setup, Config, Scraping, NLP)
- Weeks 3-4: Increments 5-7 (Event Extraction, Matching, API)
- Weeks 5-6: Increments 8-10 (Export, Frontend)
- Weeks 7-8: Increments 11-12 (Production Ready, Testing)

---

## Success Criteria

Each increment should meet these criteria before moving to the next:

✅ Code compiles/runs without errors  
✅ Unit tests pass (where applicable)  
✅ Manual testing successful  
✅ Code committed to git  
✅ Documentation updated  

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Ollama too slow | Use lighter model (llama3.2:3b or phi3:mini) or enable GPU acceleration |
| Out of memory error | Check system RAM: 16GB→llama3.1:8b, 8GB→llama3.2:3b, 4GB→gemma3:1b |
| Website blocking | Implement user-agent rotation, respect robots.txt |
| Poor extraction accuracy | Iterative prompt engineering, use examples |
| Frontend complexity | Start with minimal UI, enhance later |
| Ollama not starting | Check installation, verify port 11434 is free |

---

## Quick Start Commands

```bash
# 1. Install Ollama (one-time setup)
# Windows: Download from https://ollama.ai/download/windows
# Linux: curl -fsSL https://ollama.ai/install.sh | sh
# Mac: Download from https://ollama.ai/download/mac

# 2. Check existing models
ollama list

# 3. Pull a model if you don't have one (optional)
# For 16GB+ RAM systems (recommended):
# ollama pull llama3.1:8b
# For 8-12GB RAM systems:
# ollama pull llama3.2:3b
# (Skip if you already have llama3.1:8b or another suitable model)

# 4. Verify Ollama is running
# It should auto-start, check: http://localhost:11434

# 4. Set up backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 5. Configure your model
# Create .env file and set:
# OLLAMA_MODEL=llama3.1:8b
# (or whatever model you have installed - check with: ollama list)

# 6. Run backend
uvicorn app.main:app --reload

# 7. In new terminal - set up frontend
cd frontend
npm install
npm start

# 8. Run tests
# Backend tests
cd backend
venv\Scripts\activate
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

---

**End of Implementation Plan**
