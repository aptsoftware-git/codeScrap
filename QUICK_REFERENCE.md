# Quick Reference Card

Fast reference for common commands and workflows.

---

## 🚀 Quick Start

### Development Setup
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env           # Edit with your settings
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
cp .env.example .env           # Set API URL
npm run dev
```

### Access Points
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📝 Common Commands

### Backend

```bash
# Run development server
uvicorn app.main:app --reload

# Run production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Run tests
pytest                         # All tests
pytest -v                      # Verbose
pytest --cov=app               # With coverage
pytest -m integration          # Integration tests only
pytest -m "not slow"           # Skip slow tests
python run_tests.py --coverage # Using test runner

# Check logs
tail -f logs/app.log           # Follow logs
grep ERROR logs/app.log        # Find errors
```

### Frontend

```bash
# Development server
npm run dev

# Production build
npm run build

# Preview build
npm run preview

# Lint code
npm run lint

# Type check
npm run type-check
```

### Ollama

```bash
# List models
ollama list

# Pull model
ollama pull llama3.1:8b

# Start server
ollama serve

# Check version
curl http://localhost:11434/api/version

# Test generation
ollama run llama3.1:8b "Test prompt"
```

---

## 🔍 API Quick Reference

### Health & Status
```bash
# Health check
curl http://localhost:8000/health

# Ollama status
curl http://localhost:8000/ollama/status

# List sources
curl http://localhost:8000/sources
```

### Search
```bash
# Basic search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"phrase": "cyber attack"}'

# Search with filters
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "phrase": "protest",
    "location": "Mumbai",
    "event_type": "Protest",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }'

# Get session results
curl http://localhost:8000/search/session/{session_id}
```

### Export
```bash
# Export from session
curl -X POST http://localhost:8000/export/excel \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123"}' \
  --output events.xlsx

# Custom export
curl -X POST http://localhost:8000/export/excel/custom \
  -H "Content-Type: application/json" \
  -d '{"events": [...]}' \
  --output selected.xlsx
```

---

## 🧪 Testing Quick Reference

### Run Tests
```bash
# All tests
pytest

# Specific file
pytest tests/test_services.py

# Specific test
pytest tests/test_services.py::TestSearchService::test_calculate_relevance

# By marker
pytest -m integration         # Integration tests
pytest -m "not slow"          # Skip slow tests

# With coverage
pytest --cov=app --cov-report=html

# Using test runner
python run_tests.py           # All tests
python run_tests.py --unit    # Unit tests only
python run_tests.py --coverage # With coverage report
```

### Write Tests
```python
# Unit test
def test_my_function():
    result = my_function("input")
    assert result == "expected"

# Integration test
def test_api_endpoint():
    response = client.post("/endpoint", json={...})
    assert response.status_code == 200

# With fixture
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"

# With mock
@patch('module.function')
def test_with_mock(mock_func):
    mock_func.return_value = "mocked"
    result = my_function()
    assert result == "mocked"
```

---

## 🔧 Configuration Quick Reference

### Environment Variables

**Backend (.env):**
```bash
# Essential
DEBUG=false
LOG_LEVEL=INFO
OLLAMA_MODEL=llama3.1:8b
CORS_ORIGINS=http://localhost:5173

# Performance
MAX_CONCURRENT_SCRAPES=5
ENABLE_CACHING=true

# Security
RATE_LIMIT_SEARCH=10
RATE_LIMIT_EXPORT=5
```

**Frontend (.env):**
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=300000
```

### Sources Configuration

**config/sources.json:**
```json
{
  "sources": [
    {
      "name": "News Site",
      "url": "https://example.com/news",
      "enabled": true,
      "scrape_config": {
        "article_selector": "article.news-item",
        "title_selector": "h2.title",
        "content_selector": "div.content",
        "date_selector": "time.published",
        "link_selector": "a.read-more"
      }
    }
  ]
}
```

---

## 🐛 Debugging Quick Reference

### Check Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Find errors
grep -i error backend/logs/app.log

# Last 100 lines
tail -n 100 backend/logs/app.log
```

### Common Issues

**Ollama not connecting:**
```bash
# Check if running
curl http://localhost:11434/api/version

# Start Ollama
ollama serve
```

**CORS errors:**
```bash
# Check CORS_ORIGINS in .env
echo $CORS_ORIGINS  # Linux/Mac
echo %CORS_ORIGINS%  # Windows

# Should include frontend URL
CORS_ORIGINS=http://localhost:5173
```

**Import errors:**
```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall
pip install -r requirements.txt
```

**Port in use:**
```bash
# Find process on port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

---

## 🚢 Deployment Quick Reference

### systemd Service
```bash
# Start service
sudo systemctl start event-scraper-backend

# Stop service
sudo systemctl stop event-scraper-backend

# Restart service
sudo systemctl restart event-scraper-backend

# Check status
sudo systemctl status event-scraper-backend

# View logs
sudo journalctl -u event-scraper-backend -f
```

### Docker
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Nginx
```bash
# Test config
sudo nginx -t

# Reload config
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check logs
sudo tail -f /var/log/nginx/error.log
```

---

## 📚 Documentation Reference

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](README.md) | Project overview | Everyone |
| [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) | Completion summary | Project managers |
| [USER_GUIDE.md](doc/USER_GUIDE.md) | How to use | End users |
| [DEPLOYMENT.md](doc/DEPLOYMENT.md) | How to deploy | DevOps/Admins |
| [API.md](doc/API.md) | API reference | Developers |
| [CONFIGURATION.md](doc/CONFIGURATION.md) | Configuration | Administrators |
| [TROUBLESHOOTING.md](doc/TROUBLESHOOTING.md) | Problem-solving | Support teams |
| [DEVELOPER_GUIDE.md](doc/DEVELOPER_GUIDE.md) | Development | Developers |
| [TESTING_GUIDE.md](doc/TESTING_GUIDE.md) | Testing | QA/Developers |

---

## 📊 Event Types Reference

### Categories

**Violence & Security:**
Protest, Demonstration, Attack, Explosion, Bombing, Shooting, Theft, Kidnapping

**Cyber Events:**
Cyber Attack, Cyber Incident, Data Breach

**Meetings & Conferences:**
Conference, Meeting, Summit

**Disasters & Accidents:**
Accident, Natural Disaster

**Political & Military:**
Election, Political Event, Military Operation

**Crisis Events:**
Terrorist Activity, Civil Unrest, Humanitarian Crisis

**Other:**
Other

---

## 🔑 Key File Locations

```
backend/
├── .env                    # Environment variables
├── logs/app.log           # Application logs
├── requirements.txt       # Python dependencies
└── pytest.ini            # Test configuration

frontend/
├── .env                   # Frontend config
└── package.json          # Node dependencies

config/
└── sources.json          # News source configuration

doc/
├── API.md                # API documentation
├── DEPLOYMENT.md         # Deployment guide
├── CONFIGURATION.md      # Configuration guide
└── ...                   # Other docs
```

---

## ⌨️ VS Code Shortcuts

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

**Keyboard Shortcuts:**
- `Ctrl+Shift+P` - Command palette
- `F5` - Start debugging
- `Ctrl+`` - Toggle terminal
- `Ctrl+Shift+F` - Search in files

---

## 🎯 Performance Tuning

### For Speed
```bash
# .env
OLLAMA_MODEL=mistral:7b
MAX_CONCURRENT_SCRAPES=10
NLP_MODEL=en_core_web_sm
ENABLE_CACHING=true
```

### For Accuracy
```bash
# .env
OLLAMA_MODEL=llama2:13b
MAX_EVENTS_PER_ARTICLE=20
NLP_MODEL=en_core_web_lg
OLLAMA_TEMPERATURE=0.0
```

---

## 📞 Getting Help

1. Check [TROUBLESHOOTING.md](doc/TROUBLESHOOTING.md)
2. Review logs: `tail -f backend/logs/app.log`
3. Check API docs: http://localhost:8000/docs
4. Search documentation
5. Contact support: support@yourdomain.com

---

**Last Updated:** December 2, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
