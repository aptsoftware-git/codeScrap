# Demo Scripts

This directory contains demonstration scripts that showcase the functionality of each increment of the Web Scraper project.

## Available Demos

### 1. Entity Extraction Demo
**File:** `demo_entity_extraction.py`  
**Increment:** 4  
**Description:** Demonstrates NLP entity extraction from news articles, showing how the system identifies persons, organizations, locations, dates, and events.

**Run:**
```bash
cd backend
python demo/demo_entity_extraction.py
```

### 2. Event Extraction Demo
**File:** `demo_event_extraction.py`  
**Increment:** 5  
**Description:** Shows the complete pipeline from article text to structured event data using Ollama LLM. Demonstrates how raw articles are transformed into structured EventData objects.

**Run:**
```bash
cd backend
python demo/demo_event_extraction.py
```

### 3. Query Matching Demo
**File:** `demo_query_matching.py`  
**Increment:** 6  
**Description:** Demonstrates how events are matched and ranked based on search queries, showing relevance scoring for text, location, date, and event type.

**Run:**
```bash
cd backend
python demo/demo_query_matching.py
```

### 4. Web Scraping Demo
**File:** `demo_scraping.py`  
**Increment:** 3  
**Description:** Practical demonstration of web scraping with configured news sources, showing rate limiting and content extraction.

**Run:**
```bash
cd backend
python demo/demo_scraping.py
```

### 5. Search API Demo
**File:** `demo_search_api.py`  
**Increment:** 7  
**Description:** Visual demonstration of the complete end-to-end search pipeline, showing how the Search API coordinates scraping, extraction, and ranking.

**Run:**
```bash
cd backend
python demo/demo_search_api.py
```

### 6. Complete Workflow Demo
**File:** `demo_complete_workflow.py`  
**Increment:** 8  
**Description:** End-to-end demonstration showing the complete workflow from search query to Excel export, combining all increments.

**Run:**
```bash
cd backend
python demo/demo_complete_workflow.py
```

## Requirements

All demos require:
- Python dependencies installed (`pip install -r requirements.txt`)
- Ollama running locally (for demos 5, 7, and 8)
- Configured news sources in `config/sources.yaml`

## Path Setup

All demo scripts automatically add the backend directory to the Python path:
```python
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
```

This allows them to import from the `app` package correctly.

## Notes

- **Network Access:** Some demos make real HTTP requests to news websites
- **Rate Limiting:** Web scraping demos respect configured rate limits
- **LLM Dependency:** Event extraction and search demos require Ollama to be running
- **Educational Purpose:** These demos are designed to show system capabilities, not for production use

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'app'`, make sure you're running from the `backend/` directory:
```bash
cd backend
python demo/demo_<name>.py
```

### Ollama Not Available
If demos fail with Ollama errors:
1. Start Ollama: `ollama serve`
2. Pull the model: `ollama pull llama3.1:8b`

### Network Errors
Some demos may fail if:
- No internet connection
- News websites are blocking requests
- Rate limits are exceeded

This is expected behavior and demonstrates the system's error handling.
