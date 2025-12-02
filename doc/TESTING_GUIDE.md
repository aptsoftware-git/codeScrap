# Testing Guide

Comprehensive guide for testing the Event Scraper & Analyzer.

---

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Test Setup](#test-setup)
3. [Running Tests](#running-tests)
4. [Test Types](#test-types)
5. [Writing Tests](#writing-tests)
6. [Coverage](#coverage)
7. [Continuous Integration](#continuous-integration)

---

## Testing Strategy

### Testing Pyramid

```
        /\
       /  \
      / E2E \       End-to-End Tests (Few)
     /------\
    /        \
   /Integration\    Integration Tests (Some)
  /------------\
 /              \
/   Unit Tests   \  Unit Tests (Many)
------------------
```

**Unit Tests (70%):**
- Test individual functions/classes
- Fast execution
- Mock external dependencies
- High coverage

**Integration Tests (25%):**
- Test API endpoints
- Test service interactions
- Use TestClient
- Real components, mocked external services

**End-to-End Tests (5%):**
- Test complete workflows
- Real browser (if applicable)
- Real services
- Slow but comprehensive

### Test Coverage Goals

| Component | Coverage Goal |
|-----------|--------------|
| Services | >80% |
| API Endpoints | >90% |
| Utils | >70% |
| Overall | >75% |

---

## Test Setup

### Install Test Dependencies

```bash
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies (includes pytest)
pip install -r requirements.txt

# Verify pytest installed
pytest --version
```

### Configuration

**pytest.ini**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --cov=app
    --cov-report=term-missing
    --cov-report=html

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
```

### Test Environment

Create `.env.test` for test-specific configuration:
```bash
DEBUG=true
LOG_LEVEL=WARNING
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
ENABLE_CACHING=false
```

---

## Running Tests

### Basic Commands

**All Tests**
```bash
pytest
```

**Verbose Output**
```bash
pytest -v
```

**Very Verbose**
```bash
pytest -vv
```

**Show print statements**
```bash
pytest -s
```

**Stop at first failure**
```bash
pytest -x
```

**Run last failed tests**
```bash
pytest --lf
```

### Filter Tests

**By File**
```bash
pytest tests/test_services.py
```

**By Test Class**
```bash
pytest tests/test_services.py::TestSearchService
```

**By Test Function**
```bash
pytest tests/test_services.py::TestSearchService::test_calculate_relevance_exact_match
```

**By Marker**
```bash
# Run only integration tests
pytest -m integration

# Skip integration tests
pytest -m "not integration"

# Skip slow tests
pytest -m "not slow"
```

**By Keyword**
```bash
# Run tests matching keyword
pytest -k "search"

# Run tests NOT matching keyword
pytest -k "not ollama"
```

### Coverage Reports

**Terminal Coverage**
```bash
pytest --cov=app --cov-report=term-missing
```

**HTML Coverage Report**
```bash
pytest --cov=app --cov-report=html

# Open htmlcov/index.html in browser
```

**Coverage for Specific Module**
```bash
pytest --cov=app.services --cov-report=html
```

**Minimum Coverage Threshold**
```bash
pytest --cov=app --cov-fail-under=75
```

### Using Test Runner Script

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

# Specific file
python run_tests.py --file test_services.py

# Verbose
python run_tests.py -v
```

---

## Test Types

### Unit Tests

**Purpose:** Test individual components in isolation

**Characteristics:**
- Fast execution (<1s per test)
- No external dependencies
- Use mocks/stubs
- Deterministic results

**Example:**
```python
# tests/test_services.py
import pytest
from unittest.mock import Mock, patch
from app.services.search_service import SearchService

class TestSearchService:
    def test_calculate_relevance_exact_match(self):
        """Test relevance calculation for exact match."""
        service = SearchService()
        
        event = EventData(
            title="Cyber Attack on Banks",
            date="2025-12-01",
            location=Location(city="Mumbai", country="India"),
            event_type=EventType.CYBER_ATTACK,
            description="Major cyber attack",
            organizer=None,
            url="https://example.com",
            source_url="https://example.com"
        )
        
        query = "cyber attack banks"
        score = service.calculate_relevance(event, query)
        
        assert score > 70  # High relevance expected
    
    @patch('httpx.AsyncClient.get')
    async def test_scrape_url_success(self, mock_get):
        """Test successful URL scraping."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_get.return_value = mock_response
        
        from app.services.scraper_service import ScraperService
        scraper = ScraperService()
        result = await scraper.scrape_url("https://example.com")
        
        assert "Test" in result
```

### Integration Tests

**Purpose:** Test API endpoints and service interactions

**Characteristics:**
- Slower than unit tests (1-5s)
- Use TestClient
- Real components, mocked external services
- Test request/response

**Example:**
```python
# tests/test_integration.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestHealthEndpoints:
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_search_with_phrase_only(self):
        """Test basic search with just phrase."""
        response = client.post(
            "/search",
            json={"phrase": "test event"}
        )
        
        assert response.status_code in [200, 500, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "matching_events" in data
            assert isinstance(data["matching_events"], list)
```

### End-to-End Tests

**Purpose:** Test complete workflows from user perspective

**Characteristics:**
- Slowest (10-60s)
- Real services
- Complete user workflows
- Catch integration issues

**Example:**
```python
# tests/test_e2e.py
class TestEndToEndWorkflow:
    def test_search_and_export_workflow(self):
        """Test complete search -> export workflow."""
        # Step 1: Search
        search_response = client.post(
            "/search",
            json={"phrase": "technology conference"}
        )
        
        assert search_response.status_code == 200
        session_id = search_response.json()["session_id"]
        
        # Step 2: Verify session
        session_response = client.get(f"/search/session/{session_id}")
        assert session_response.status_code == 200
        
        # Step 3: Export
        export_response = client.post(
            "/export/excel",
            json={"session_id": session_id}
        )
        
        assert export_response.status_code == 200
        assert len(export_response.content) > 0
```

---

## Writing Tests

### Test Structure

**AAA Pattern: Arrange, Act, Assert**
```python
def test_example():
    # Arrange - Set up test data
    service = MyService()
    input_data = "test input"
    
    # Act - Execute the code under test
    result = service.process(input_data)
    
    # Assert - Verify the result
    assert result == "expected output"
```

### Naming Conventions

**Test Files**
- Prefix with `test_`
- Examples: `test_services.py`, `test_integration.py`

**Test Classes**
- Prefix with `Test`
- Group related tests
- Example: `TestSearchService`

**Test Functions**
- Prefix with `test_`
- Descriptive names
- Examples:
  - `test_calculate_relevance_exact_match`
  - `test_scrape_url_timeout`
  - `test_export_empty_events`

### Fixtures

**Basic Fixture**
```python
import pytest

@pytest.fixture
def sample_event():
    """Provide a sample event for testing."""
    return EventData(
        title="Sample Event",
        date="2025-12-01",
        location=Location(city="Mumbai", country="India"),
        event_type=EventType.PROTEST,
        description="Test event",
        organizer="Test Org",
        url="https://example.com",
        source_url="https://example.com"
    )

def test_using_fixture(sample_event):
    """Test using the fixture."""
    assert sample_event.title == "Sample Event"
```

**Fixture Scopes**
```python
# Function scope (default) - new instance per test
@pytest.fixture
def resource():
    return create_resource()

# Class scope - shared within test class
@pytest.fixture(scope="class")
def shared_resource():
    return create_resource()

# Module scope - shared within module
@pytest.fixture(scope="module")
def module_resource():
    return create_resource()

# Session scope - shared across all tests
@pytest.fixture(scope="session")
def session_resource():
    return create_resource()
```

**Setup/Teardown**
```python
@pytest.fixture
def database():
    """Fixture with setup and teardown."""
    # Setup
    db = create_database()
    db.connect()
    
    yield db  # Provide to test
    
    # Teardown
    db.disconnect()
    db.cleanup()
```

### Mocking

**Mock Function**
```python
from unittest.mock import Mock, patch

@patch('app.services.scraper_service.httpx.get')
def test_with_mock(mock_get):
    """Test with mocked HTTP call."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "Mocked content"
    
    # Test code using httpx.get
    # Will use mocked version
```

**Mock Class**
```python
@patch('app.services.ollama_service.OllamaClient')
def test_with_mocked_class(mock_ollama):
    """Test with mocked Ollama client."""
    mock_instance = Mock()
    mock_instance.generate.return_value = "Generated text"
    mock_ollama.return_value = mock_instance
    
    # Test code
```

**Multiple Mocks**
```python
@patch('module.function2')
@patch('module.function1')
def test_multiple_mocks(mock1, mock2):
    """Test with multiple mocks."""
    mock1.return_value = "value1"
    mock2.return_value = "value2"
    
    # Test code
```

### Parametrized Tests

**Run same test with different inputs**
```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_with_parameters(input, expected):
    """Test with multiple parameter sets."""
    result = process(input)
    assert result == expected
```

**Multiple Parameters**
```python
@pytest.mark.parametrize("phrase,location,expected_count", [
    ("cyber attack", "India", 5),
    ("protest", "Mumbai", 3),
    ("conference", "USA", 10),
])
def test_search_variations(phrase, location, expected_count):
    """Test search with different parameters."""
    response = client.post(
        "/search",
        json={"phrase": phrase, "location": location}
    )
    
    assert len(response.json()["matching_events"]) >= expected_count
```

### Test Markers

**Mark slow tests**
```python
@pytest.mark.slow
def test_slow_operation():
    """This test takes a long time."""
    # Slow operation
    pass
```

**Mark integration tests**
```python
@pytest.mark.integration
def test_api_integration():
    """Integration test."""
    pass
```

**Skip test**
```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """Future feature test."""
    pass
```

**Skip conditionally**
```python
import sys

@pytest.mark.skipif(sys.platform == "win32", reason="Linux only")
def test_linux_specific():
    """Test for Linux only."""
    pass
```

**Expected to fail**
```python
@pytest.mark.xfail(reason="Known bug")
def test_known_issue():
    """Test for known bug."""
    # Will be marked as xfail, not failure
    pass
```

---

## Coverage

### Viewing Coverage

**Terminal Report**
```bash
pytest --cov=app --cov-report=term-missing

# Output shows:
# - Lines covered
# - Lines missing
# - Coverage percentage
```

**HTML Report**
```bash
pytest --cov=app --cov-report=html

# Open htmlcov/index.html
# Interactive coverage report
# Click files to see uncovered lines
```

**XML Report (for CI)**
```bash
pytest --cov=app --cov-report=xml

# Generates coverage.xml
# Used by CI systems
```

### Improving Coverage

**Identify Uncovered Code**
```bash
pytest --cov=app --cov-report=term-missing

# Look for "Missing" column
# Shows line numbers not covered
```

**Add Tests for Uncovered Lines**
```python
# If lines 45-50 are uncovered, write test to cover them
def test_error_case():
    """Test the error handling path."""
    # This test should execute lines 45-50
    with pytest.raises(ValueError):
        service.method_that_raises_error()
```

**Coverage Reports by Module**
```bash
pytest --cov=app.services --cov-report=html
```

### Coverage Best Practices

✅ **DO:**
- Aim for >75% overall coverage
- Focus on critical paths (100% coverage)
- Test error handling
- Test edge cases
- Review coverage reports regularly

❌ **DON'T:**
- Chase 100% coverage blindly
- Test trivial getters/setters
- Write tests just for coverage
- Ignore hard-to-test code

---

## Continuous Integration

### GitHub Actions Example

**.github/workflows/test.yml**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        python -m spacy download en_core_web_sm
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./backend/coverage.xml
```

### Pre-commit Hooks

**.pre-commit-config.yaml**
```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

---

## Troubleshooting Tests

### Tests Fail Locally

**Check Environment**
```bash
# Verify virtual environment activated
which python  # Linux/Mac
where python  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Check Configuration**
```bash
# Verify .env file exists
cat .env  # Linux/Mac
type .env  # Windows

# Check test environment
cat .env.test
```

### Import Errors

```bash
# Ensure app is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac

# Or run from backend directory
cd backend
pytest
```

### Ollama Tests Fail

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Skip Ollama tests if not available
pytest -m "not ollama"
```

### Slow Tests

```bash
# Skip slow tests during development
pytest -m "not slow"

# Run only fast tests
pytest -m "not slow and not integration"
```

---

## Best Practices

### General

1. **Write tests first (TDD)** - Define behavior before implementation
2. **One assertion per test** - Makes failures clear
3. **Independent tests** - Tests should not depend on each other
4. **Descriptive names** - Test name should describe what it tests
5. **Fast tests** - Keep tests fast for quick feedback

### Specific to This Project

1. **Mock Ollama** - LLM calls are slow and non-deterministic
2. **Mock scraping** - Don't hit real websites in tests
3. **Use fixtures** - Reuse common test data
4. **Test edge cases** - Empty lists, null values, special characters
5. **Test error handling** - Verify graceful failures

---

**Last Updated:** December 2, 2025  
**Version:** 1.0.0
