# Developer Guide

Complete guide for developers working on the Event Scraper & Analyzer.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Code Structure](#code-structure)
3. [Development Setup](#development-setup)
4. [Adding Features](#adding-features)
5. [Testing](#testing)
6. [Code Standards](#code-standards)
7. [Common Tasks](#common-tasks)
8. [Debugging](#debugging)

---

## Architecture Overview

### System Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │──────▶│   FastAPI    │──────▶│   Ollama    │
│  Frontend   │ HTTP  │   Backend    │ HTTP  │   LLM       │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            │
                     ┌──────┴──────┐
                     │             │
                  ┌──▼───┐    ┌───▼──┐
                  │spaCy │    │News  │
                  │ NLP  │    │Sites │
                  └──────┘    └──────┘
```

### Component Responsibilities

**Frontend (React + TypeScript)**
- User interface (search form, results display)
- API communication via Axios
- State management
- Excel file downloads

**Backend (FastAPI + Python)**
- RESTful API endpoints
- Orchestration of services
- Session management
- CORS and security

**Services Layer**
- **OllamaService**: LLM integration for event extraction
- **ScraperService**: Web scraping from configured sources
- **NLPService**: Entity extraction using spaCy
- **SearchService**: Query matching and relevance scoring
- **ExportService**: Excel file generation

**External Services**
- **Ollama**: Local LLM server (llama3.1:8b)
- **News Sources**: Configured websites to scrape

---

## Code Structure

### Backend Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, routes, middleware
│   ├── config.py            # Pydantic models, EventType enum
│   ├── settings.py          # Environment-based configuration
│   │
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── ollama_service.py      # LLM integration
│   │   ├── scraper_service.py     # Web scraping
│   │   ├── nlp_service.py         # spaCy NER
│   │   ├── search_service.py      # Query matching
│   │   └── export_service.py      # Excel export
│   │
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── logger.py        # Logging configuration
│
├── tests/                   # Test files
│   ├── __init__.py
│   ├── test_integration.py  # Integration tests
│   ├── test_services.py     # Service unit tests
│   ├── test_increment*.py   # Increment-specific tests
│   └── test_*.py           # Other test files
│
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
├── run_tests.py            # Test runner script
└── .env.example            # Environment template
```

### Frontend Structure

```
frontend/
├── src/
│   ├── App.tsx             # Main application component
│   │
│   ├── components/         # React components
│   │   ├── SearchForm.tsx         # Search interface
│   │   ├── EventList.tsx          # Results list
│   │   ├── EventCard.tsx          # Individual event
│   │   └── ExportButton.tsx       # Export functionality
│   │
│   ├── services/           # API client
│   │   └── api.ts          # Axios API calls
│   │
│   ├── types/              # TypeScript types
│   │   └── index.ts        # Type definitions
│   │
│   └── index.tsx           # Entry point
│
├── package.json            # Dependencies
└── .env.example           # Frontend config
```

---

## Development Setup

### Prerequisites

```bash
# Required software
- Python 3.8+ (recommended: 3.11)
- Node.js 16+ (recommended: 18)
- Ollama (download from https://ollama.com)
- Git
```

### Initial Setup

**1. Clone Repository**
```bash
git clone <repository-url>
cd event-scraper
```

**2. Setup Backend**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create .env from example
cp .env.example .env

# Edit .env with your settings
```

**3. Setup Frontend**
```bash
cd frontend

# Install dependencies
npm install

# Create .env from example
cp .env.example .env

# Edit .env with API URL
```

**4. Setup Ollama**
```bash
# Download model
ollama pull llama3.1:8b

# Verify
ollama list

# Check running
curl http://localhost:11434/api/version
```

**5. Configure Sources**
```bash
# Edit config/sources.json
# Add your news sources with CSS selectors
```

### Running Development Servers

**Terminal 1: Backend**
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Adding Features

### Adding a New API Endpoint

**1. Define Pydantic Models (if needed)**
```python
# In app/config.py
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    param1: str
    param2: int

class NewFeatureResponse(BaseModel):
    result: str
    status: str
```

**2. Create Service Method**
```python
# In app/services/new_service.py
class NewService:
    def process(self, param1: str, param2: int) -> dict:
        """Process the new feature."""
        # Your logic here
        return {"result": "success"}
```

**3. Add API Route**
```python
# In app/main.py
from app.services.new_service import NewService

@app.post("/api/v1/new-feature", response_model=NewFeatureResponse)
async def new_feature(request: NewFeatureRequest):
    """New feature endpoint."""
    service = NewService()
    result = service.process(request.param1, request.param2)
    return NewFeatureResponse(**result)
```

**4. Write Tests**
```python
# In tests/test_new_feature.py
def test_new_feature():
    from app.services.new_service import NewService
    
    service = NewService()
    result = service.process("test", 42)
    
    assert result["result"] == "success"
```

**5. Update Documentation**
```markdown
# In doc/API.md
### POST /api/v1/new-feature

**Description:** New feature endpoint

**Request:**
```json
{
  "param1": "value",
  "param2": 42
}
```

**Response:**
```json
{
  "result": "success",
  "status": "ok"
}
```
```

### Adding a New Event Type

**1. Update Backend Enum**
```python
# In app/config.py
class EventType(str, Enum):
    # Existing types...
    NEW_TYPE = "New Type"
```

**2. Update Frontend Enum**
```typescript
// In frontend/src/types/index.ts
export enum EventType {
  // Existing types...
  NEW_TYPE = "New Type"
}
```

**3. Update Search Form**
```typescript
// In frontend/src/components/SearchForm.tsx
// Add to eventTypeOptions array
const eventTypeOptions = [
  // Existing options...
  { value: EventType.NEW_TYPE, label: "New Type", category: "Your Category" }
];
```

**4. Update Documentation**
```markdown
# Update doc/USER_GUIDE.md, doc/API.md
# Add new event type to the list
```

### Adding a New News Source

**1. Inspect the Website**
- Open browser DevTools (F12)
- Find CSS selectors for:
  - Article container
  - Title
  - Content/description
  - Date
  - Link to full article

**2. Test Selectors**
```javascript
// In browser console
document.querySelectorAll('article.news-item')  // Test article selector
document.querySelector('h2.title')?.textContent  // Test title
```

**3. Add to sources.json**
```json
{
  "sources": [
    {
      "name": "New Source",
      "url": "https://newssite.com/latest",
      "enabled": true,
      "scrape_config": {
        "article_selector": "article.news-item",
        "title_selector": "h2.title",
        "content_selector": "div.content",
        "date_selector": "time.published",
        "link_selector": "a.read-more",
        "date_format": "%Y-%m-%d"
      }
    }
  ]
}
```

**4. Test the Source**
```bash
# Check if source is loaded
curl http://localhost:8000/sources

# Test with a search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"phrase": "test"}'
```

---

## Testing

### Test Types

**Unit Tests**
- Test individual functions/classes
- Use mocks for external dependencies
- Fast execution
- Located in `tests/test_services.py`

**Integration Tests**
- Test API endpoints end-to-end
- Use TestClient
- May require running services
- Located in `tests/test_integration.py`

**Increment Tests**
- Test specific increment functionality
- Located in `tests/test_increment*.py`

### Running Tests

**All Tests**
```bash
cd backend
pytest
```

**With Coverage**
```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

**Specific Test File**
```bash
pytest tests/test_services.py
```

**Specific Test**
```bash
pytest tests/test_services.py::TestSearchService::test_calculate_relevance_exact_match
```

**Skip Slow Tests**
```bash
pytest -m "not slow"
```

**Only Integration Tests**
```bash
pytest -m integration
```

**Using Test Runner**
```bash
# All tests
python run_tests.py

# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# With coverage
python run_tests.py --coverage

# Skip slow tests
python run_tests.py --fast
```

### Writing Tests

**Unit Test Example**
```python
# tests/test_my_service.py
import pytest
from app.services.my_service import MyService

class TestMyService:
    def test_basic_functionality(self):
        """Test basic functionality."""
        service = MyService()
        result = service.process("input")
        assert result == "expected"
    
    def test_error_handling(self):
        """Test error handling."""
        service = MyService()
        with pytest.raises(ValueError):
            service.process(None)
```

**Integration Test Example**
```python
# tests/test_integration.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_endpoint():
    """Test API endpoint."""
    response = client.post(
        "/search",
        json={"phrase": "test"}
    )
    assert response.status_code == 200
    assert "matching_events" in response.json()
```

### Test Coverage Goals

- **Overall:** >70%
- **Services:** >80%
- **Critical Paths:** 100%

---

## Code Standards

### Python Code Style

**PEP 8 Compliance**
```python
# Good
def calculate_relevance(event: EventData, query: str) -> float:
    """Calculate relevance score for event."""
    pass

# Bad
def calc_rel(e, q):
    pass
```

**Type Hints**
```python
# Always use type hints
def process_event(event: EventData) -> dict:
    return {"status": "ok"}
```

**Docstrings**
```python
def extract_entities(text: str) -> ExtractedEntities:
    """
    Extract named entities from text using spaCy.
    
    Args:
        text: Input text to process
        
    Returns:
        ExtractedEntities with persons, orgs, locations, dates
    """
    pass
```

### TypeScript Code Style

**Interface Definitions**
```typescript
// Always define interfaces for data
interface EventData {
  title: string;
  date: string;
  location: Location;
  eventType: EventType;
}
```

**Component Structure**
```typescript
// Functional components with TypeScript
import React from 'react';

interface Props {
  events: EventData[];
  onSelect: (event: EventData) => void;
}

export const EventList: React.FC<Props> = ({ events, onSelect }) => {
  return (
    // JSX
  );
};
```

### Commit Messages

```bash
# Format: <type>(<scope>): <message>

# Examples:
feat(search): add date range filtering
fix(export): handle special characters in Excel
docs(api): update endpoint documentation
test(services): add unit tests for NLP service
refactor(scraper): improve error handling
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance

---

## Common Tasks

### Adding a Configuration Variable

**1. Add to .env.example**
```bash
# In backend/.env.example
NEW_SETTING=default_value
```

**2. Add to Settings class**
```python
# In app/settings.py
class Settings(BaseSettings):
    # Existing settings...
    new_setting: str = "default_value"
```

**3. Use in Code**
```python
from app.settings import settings

value = settings.new_setting
```

**4. Document**
```markdown
# In doc/CONFIGURATION.md
### NEW_SETTING
Default: `default_value`
Purpose: Description of what it does
Example: `NEW_SETTING=custom_value`
```

### Updating Dependencies

**Backend**
```bash
# Update specific package
pip install --upgrade package-name

# Update all (careful!)
pip list --outdated
pip install --upgrade package-name1 package-name2

# Update requirements.txt
pip freeze > requirements.txt
```

**Frontend**
```bash
# Check outdated packages
npm outdated

# Update specific package
npm update package-name

# Update all (careful!)
npm update

# Update package.json
npm install package-name@latest
```

### Database Migrations (Future)

```python
# If adding database later
# Use Alembic for migrations

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Debugging

### Backend Debugging

**Enable Debug Mode**
```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
```

**Add Logging**
```python
from app.utils.logger import logger

logger.debug(f"Processing event: {event.title}")
logger.info("Search completed")
logger.warning("Slow response from source")
logger.error(f"Failed to parse: {error}")
```

**Use pdb Debugger**
```python
import pdb

def my_function():
    # Code...
    pdb.set_trace()  # Debugger breakpoint
    # More code...
```

**VS Code Debugging**
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload"
      ],
      "jinja": true
    }
  ]
}
```

### Frontend Debugging

**Browser DevTools**
```typescript
// Add console logs
console.log('Search params:', params);
console.error('API error:', error);

// Debugger breakpoint
debugger;
```

**React DevTools**
- Install React DevTools browser extension
- Inspect component props and state
- Track re-renders

**Network Debugging**
- Open DevTools Network tab
- Monitor API calls
- Check request/response

### Common Issues

**Issue: Ollama Not Connecting**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama
ollama serve

# Check logs
tail -f backend/logs/app.log
```

**Issue: CORS Errors**
```bash
# Check CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:5173

# Restart backend
```

**Issue: Import Errors**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Performance Optimization

### Backend Optimization

**Async Operations**
```python
# Use async for I/O operations
async def scrape_sources(sources: List[Source]):
    tasks = [scrape_url(source.url) for source in sources]
    results = await asyncio.gather(*tasks)
    return results
```

**Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_operation(param: str) -> dict:
    # Cached result
    pass
```

**Database Indexing (if using DB)**
```python
# Add indexes to frequently queried fields
# In SQLAlchemy models
class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)  # Index for date queries
    event_type = Column(String, index=True)  # Index for filtering
```

### Frontend Optimization

**Code Splitting**
```typescript
// Lazy load components
const EventList = React.lazy(() => import('./components/EventList'));
```

**Memoization**
```typescript
import { useMemo } from 'react';

const filteredEvents = useMemo(
  () => events.filter(e => e.relevance_score > 50),
  [events]
);
```

**Debouncing**
```typescript
import { debounce } from 'lodash';

const debouncedSearch = debounce(
  (query) => performSearch(query),
  500
);
```

---

## Contributing

### Pull Request Process

1. Create feature branch from `main`
2. Make changes with clear commits
3. Write/update tests
4. Update documentation
5. Run tests and ensure they pass
6. Create pull request
7. Wait for code review
8. Address feedback
9. Merge after approval

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

---

## Resources

**Documentation:**
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [spaCy Docs](https://spacy.io/)
- [Ollama Docs](https://ollama.com/docs)

**Project Documentation:**
- [API.md](API.md) - API reference
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Troubleshooting

---

**Last Updated:** December 2, 2025  
**Version:** 1.0.0
