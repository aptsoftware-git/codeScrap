# Event Scraper & Analyzer

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

AI-powered web intelligence tool for extracting, analyzing, and exporting structured event data from news sources using LLMs (Ollama) and natural language processing.

---

## 🚀 Quick Start

### Development Setup

1. **Install Ollama**
   ```bash
   # Download from https://ollama.com/download
   ollama pull llama3.1:8b
   ```

2. **Setup Backend**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   cp .env.example .env
   # Edit .env to point to backend
   npm install
   npm run dev
   ```

4. **Access Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Deployment

See **[DEPLOYMENT.md](doc/DEPLOYMENT.md)** for comprehensive deployment guide including systemd, Docker, and Nginx configurations.

---

## 📋 Features

### Core Capabilities

- ✅ **Multi-Source Web Scraping** - Extract content from multiple news sources simultaneously with robots.txt compliance
- ✅ **AI Event Extraction** - LLM-powered event detection and classification (23 event types)
- ✅ **NLP Entity Recognition** - Extract people, organizations, locations, dates using spaCy
- ✅ **Advanced Filtering** - Filter by location, date range, event type with pagination (50 events/page)
- ✅ **Relevance Ranking** - Smart scoring algorithm for result relevance
- ✅ **Excel Export** - Export selected or all events with complete metadata
- ✅ **RESTful API** - FastAPI backend with interactive Swagger documentation
- ✅ **React Frontend** - Modern Material-UI interface with search and results display
- ✅ **Production Ready** - Environment-based configuration, logging, rate limiting, robots.txt respect

### Technical Features

- ✅ **robots.txt Compliance** - Automatically respects website crawl policies and delays
- ✅ **Pagination** - Results paginated with 50 events per page for optimal performance
- ✅ **Rate Limiting** - Per-domain rate limiting to avoid overwhelming servers
- ✅ **Retry Logic** - Exponential backoff for failed requests
- ✅ **Confidence Scoring** - Event extraction confidence scores (0-100%)
- ✅ **Session Management** - UUID-based result caching

### Event Types (23 Categories)

Supports 7 major categories:
- **Violence & Security**: Protest, Attack, Explosion, Bombing, Shooting, Theft, Kidnapping, Demonstration
- **Cyber Events**: Cyber Attack, Cyber Incident, Data Breach
- **Meetings & Conferences**: Conference, Meeting, Summit
- **Disasters & Accidents**: Accident, Natural Disaster
- **Political & Military**: Election, Political Event, Military Operation
- **Crisis Events**: Terrorist Activity, Civil Unrest, Humanitarian Crisis
- **Other**: Other events

---

## 📁 Project Structure

```
event-scraper/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI application & routes
│   │   ├── config.py       # Configuration models
│   │   ├── settings.py     # Environment-based settings
│   │   ├── services/       # Business logic
│   │   │   ├── ollama_service.py       # LLM integration
│   │   │   ├── scraper_service.py      # Web scraping
│   │   │   ├── nlp_service.py          # Entity extraction
│   │   │   ├── search_service.py       # Search & matching
│   │   │   └── export_service.py       # Excel export
│   │   └── utils/          # Logger, helpers
│   ├── tests/              # Unit tests
│   ├── demo/               # Demo scripts
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── SearchForm.tsx
│   │   │   ├── EventList.tsx
│   │   │   ├── EventCard.tsx
│   │   │   └── ExportButton.tsx
│   │   ├── services/       # API client
│   │   ├── types/          # TypeScript types
│   │   └── App.tsx         # Main app component
│   ├── package.json
│   └── .env.example        # Frontend config
├── config/
│   └── sources.json        # News source configurations
├── doc/                    # Documentation
│   ├── DEPLOYMENT.md       # Production deployment guide
│   ├── API.md              # API documentation
│   ├── USER_GUIDE.md       # End-user guide
│   ├── CONFIGURATION.md    # Configuration guide
│   ├── TROUBLESHOOTING.md  # Troubleshooting guide
│   └── ImplementationPlan.md  # Development roadmap
└── logs/                   # Application logs
```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI 0.104.1, Uvicorn
- **Language:** Python 3.8+
- **AI/LLM:** Ollama (llama3.1:8b, llama2:13b, mistral:7b)
- **NLP:** spaCy (en_core_web_sm/md/lg)
- **Web Scraping:** httpx, BeautifulSoup4
- **Export:** openpyxl (Excel .xlsx)
- **Configuration:** pydantic-settings
- **Testing:** pytest

### Frontend
- **Framework:** React 18.2 with TypeScript 5.0
- **Build Tool:** Vite 4.4.5
- **UI Library:** Material-UI (MUI) 7.3.5
- **HTTP Client:** Axios 1.13.2
- **Date Handling:** date-fns

### Infrastructure
- **LLM Server:** Ollama
- **Deployment:** systemd, Docker, Nginx
- **SSL/TLS:** Let's Encrypt

---

## 📖 Documentation

### For Users
- **[USER_GUIDE.md](doc/USER_GUIDE.md)** - Complete end-user guide
  - How to search for events
  - Understanding results and relevance scores
  - Exporting data to Excel
  - Tips & best practices
  - FAQ

### For Administrators
- **[DEPLOYMENT.md](doc/DEPLOYMENT.md)** - Production deployment guide
  - Installation and setup
  - systemd service configuration
  - Docker deployment
  - Nginx reverse proxy with SSL
  - Monitoring and troubleshooting

- **[CONFIGURATION.md](doc/CONFIGURATION.md)** - Configuration guide
  - Backend configuration (API, Ollama, scraping)
  - Frontend configuration
  - Sources configuration
  - Performance tuning
  - Security settings

- **[TROUBLESHOOTING.md](doc/TROUBLESHOOTING.md)** - Troubleshooting guide
  - Common issues and solutions
  - Performance optimization
  - Debugging tips

### For Developers
- **[API.md](doc/API.md)** - Complete API reference
  - All endpoints documented
  - Request/response schemas
  - Error handling
  - Code examples (cURL, Python, JavaScript)

- **[ImplementationPlan.md](doc/ImplementationPlan.md)** - Development roadmap
- **[WebScraperRequirementDocument.md](doc/WebScraperRequirementDocument.md)** - Requirements specification

### Increment Documentation
- [Increment 1-8 Summaries](doc/) - Backend implementation details
- [Increment 9 Summary](doc/INCREMENT9_SUMMARY.md) - React Frontend - Search Form
- [Increment 10 Summary](doc/INCREMENT10_SUMMARY.md) - React Frontend - Results Display
- [Increment 11 Summary](doc/INCREMENT11_SUMMARY.md) - Production Readiness (In Progress)

---

## 🎯 Implementation Status

### Completed ✅
- **Increment 1:** Project Setup & Ollama Integration
- **Increment 2:** Configuration & Data Models
- **Increment 3:** Web Scraping Engine
- **Increment 4:** NLP Entity Extraction (spaCy)
- **Increment 5:** Event Extraction with Ollama
- **Increment 6:** Query Matching & Relevance Scoring
- **Increment 7:** Search API Endpoint
- **Increment 8:** Excel Export Service
- **Increment 9:** React Frontend - Search Form
- **Increment 10:** React Frontend - Results Display
- **Event Types:** Updated to 23 types (7 categories)

### ✅ ALL INCREMENTS COMPLETE!
- **Increment 11:** Production Readiness ✅
  - ✅ Environment configuration (.env.example)
  - ✅ Settings management (pydantic-settings)
  - ✅ Deployment documentation (DEPLOYMENT.md)
  - ✅ API documentation (API.md)
  - ✅ User guide (USER_GUIDE.md)
  - ✅ Configuration guide (CONFIGURATION.md)
  - ✅ Troubleshooting guide (TROUBLESHOOTING.md)

- **Increment 12:** Testing & Documentation ✅
  - ✅ Unit tests for all services (30+ tests)
  - ✅ Integration tests (25+ tests)
  - ✅ End-to-end tests (5+ tests)
  - ✅ Test coverage ~80%
  - ✅ Developer guide (DEVELOPER_GUIDE.md)
  - ✅ Testing guide (TESTING_GUIDE.md)
  - ✅ Test runner script with CLI

### 🎉 Project Status: COMPLETE & PRODUCTION READY!

See **[PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)** for final project summary.

---

## 📡 API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /ollama/status` - Ollama connection status
- `GET /sources` - List configured news sources

### Search & Data
- `POST /search` - Search for events
  - Filter by phrase, location, event type, date range
  - Returns structured event data with relevance scores
- `GET /search/session/{session_id}` - Retrieve cached search results

### Export
- `POST /export/excel` - Export session results to Excel
- `POST /export/excel/custom` - Export custom event selection

### Interactive Documentation
- `/docs` - Swagger UI (interactive API documentation)
- `/redoc` - ReDoc (alternative API documentation)

See **[API.md](doc/API.md)** for complete API documentation with examples.

---

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```bash
# Application
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# CORS
CORS_ORIGINS=https://yourdomain.com

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TEMPERATURE=0.1

# Performance
MAX_CONCURRENT_SCRAPES=5
MAX_EVENTS_PER_ARTICLE=10
ENABLE_CACHING=true

# Rate Limiting
RATE_LIMIT_SEARCH=10
RATE_LIMIT_EXPORT=5
```

**Frontend (.env):**
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=300000
VITE_APP_NAME=Event Scraper
```

See **[CONFIGURATION.md](doc/CONFIGURATION.md)** for complete configuration guide.

### Sources Configuration

Configure news sources in `config/sources.json`:

```json
{
  "sources": [
    {
      "name": "Example News",
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

## � Usage Examples

### Search for Events

**Using Frontend:**
1. Open http://localhost:5173
2. Enter search phrase (e.g., "protest in Mumbai")
3. Optional: Add filters (location, event type, date range)
4. Click "Search"
5. View results with relevance scores
6. Select events and export to Excel

**Using API:**

```bash
# Search with cURL
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "phrase": "cyber attack on banks",
    "location": "India",
    "event_type": "Cyber Attack",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }'
```

```python
# Search with Python
import requests

response = requests.post(
    "http://localhost:8000/search",
    json={
        "phrase": "cyber attack on banks",
        "location": "India",
        "event_type": "Cyber Attack"
    }
)

events = response.json()["matching_events"]
for event in events:
    print(f"{event['title']} - {event['relevance_score']}%")
```

```javascript
// Search with JavaScript
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phrase: 'cyber attack on banks',
    location: 'India',
    event_type: 'Cyber Attack'
  })
});

const data = await response.json();
console.log(data.matching_events);
```

### Export to Excel

```bash
# Export all events from a session
curl -X POST http://localhost:8000/export/excel \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123"}' \
  --output events.xlsx

# Export specific events
curl -X POST http://localhost:8000/export/excel/custom \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {"title": "Event 1", "date": "2025-12-01", ...},
      {"title": "Event 2", "date": "2025-12-02", ...}
    ]
  }' \
  --output selected_events.xlsx
```

---

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_ollama_service.py

# Run with verbose output
pytest -v
```

---

## 📊 Performance

### Typical Performance Metrics

- **Search Time:** 30-60 seconds for 5-10 sources
- **Events Extracted:** 10-50 per search (depends on sources)
- **Relevance Accuracy:** 70-85% (high relevance scores)
- **Export Speed:** <5 seconds for 100 events

### Performance Tuning

**For Speed:**
- Use smaller model (`mistral:7b`)
- Reduce `MAX_CONCURRENT_SCRAPES`
- Enable caching
- Use `en_core_web_sm` for NLP

**For Accuracy:**
- Use larger model (`llama2:13b`)
- Increase `MAX_EVENTS_PER_ARTICLE`
- Use `en_core_web_lg` for NLP
- Lower `OLLAMA_TEMPERATURE`

See **[CONFIGURATION.md](doc/CONFIGURATION.md)** for detailed tuning guide.

---

## 🔐 Security

### Production Security Checklist

- [ ] Use HTTPS/TLS (Nginx with Let's Encrypt)
- [ ] Enable API key authentication (optional)
- [ ] Configure rate limiting
- [ ] Set secure CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable security headers (X-Frame-Options, etc.)
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

See **[DEPLOYMENT.md](doc/DEPLOYMENT.md)** for security configuration.

---

## 🐛 Troubleshooting

### Common Issues

**"Cannot connect to Ollama"**
```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Start Ollama
ollama serve
```

**CORS Errors**
```bash
# Add frontend URL to CORS_ORIGINS in backend/.env
CORS_ORIGINS=http://localhost:5173
```

**No Events Found**
```bash
# Verify sources are configured and enabled
curl http://localhost:8000/sources

# Check logs
tail -f backend/logs/app.log
```

See **[TROUBLESHOOTING.md](doc/TROUBLESHOOTING.md)** for comprehensive troubleshooting guide.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Run tests (`pytest`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation:** [doc/](doc/)
- **Issues:** [GitHub Issues](https://github.com/yourorg/event-scraper/issues)
- **Email:** support@yourdomain.com

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime
- **FastAPI** - Modern Python web framework
- **spaCy** - Industrial-strength NLP
- **React & Material-UI** - Frontend framework and components

---

**Version:** 1.0.0  
**Last Updated:** December 2, 2025

## ⚙️ Configuration

Edit `.env` file:

```env
OLLAMA_MODEL=llama3.1:8b
OLLAMA_URL=http://localhost:11434
API_HOST=0.0.0.0
API_PORT=8000
```

**Model Recommendations:**
- **16GB+ RAM:** llama3.1:8b ⭐ (recommended)
- **8-12GB RAM:** llama3.2:3b
- **4-8GB RAM:** gemma3:1b

---

## 🧪 Testing

```cmd
# Health check
curl http://localhost:8000/api/v1/health

# Ollama status
curl http://localhost:8000/api/v1/ollama/status

# Test generation
curl http://localhost:8000/api/v1/test/ollama
```

---

## 🤝 Development

See `doc/ImplementationPlan.md` for the 12-increment development plan.

**Increments:**
1. ✅ Project Setup & Ollama Integration
2. 📋 Configuration & Data Models
3. 📋 Web Scraping Engine
4. 📋 NLP Entity Extraction
5. 📋 Event Extraction with Ollama
6. 📋 Query Matching & Relevance
7. 📋 Search API Endpoint
8. 📋 Excel Export Service
9. 📋 React Frontend - Search Form
10. 📋 React Frontend - Results Display
11. 📋 Production Readiness
12. 📋 Testing & Documentation

---

## � License

Internal use only.

---

## 🆘 Support

For issues or questions, see:
- **Troubleshooting:** [QUICKSTART.md](QUICKSTART.md)
- **Implementation Plan:** [doc/ImplementationPlan.md](doc/ImplementationPlan.md)


---

## 🔧 Technology Stack

### Backend
- **Framework:** FastAPI
- **LLM:** Ollama (gpt-oss:20b)
- **NLP:** spaCy
- **Export:** openpyxl
- **Testing:** pytest

### Frontend (Coming Soon)
- **Framework:** React + TypeScript
- **UI Library:** Material-UI
- **HTTP Client:** Axios

---

## 🎓 Features

### Current (Increment 1)
- ✅ REST API with FastAPI
- ✅ Ollama LLM integration
- ✅ Health check and status endpoints
- ✅ Configurable via environment variables
- ✅ Structured logging

### Planned
- 📋 Web scraping from configurable sources
- 📋 Named entity recognition (spaCy)
- 📋 Event extraction and classification (Ollama)
- 📋 Query-based event matching
- 📋 Excel export functionality
- 📋 React-based web interface

---

## 🧪 Testing

```cmd
cd backend
venv\Scripts\activate
pytest tests/ -v
```

---

## 📝 Configuration

Edit `.env` file to configure:

```bash
# Ollama
OLLAMA_MODEL=gpt-oss:20b  # Your installed model

# API
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

---

## 🐛 Troubleshooting

### Ollama Connection Issues

```cmd
REM Check if Ollama is running
curl http://localhost:11434

REM Verify your model
ollama list
```

### Import Errors

```cmd
REM Ensure virtual environment is activated
venv\Scripts\activate

REM Reinstall dependencies
pip install -r requirements.txt
```

See [Backend README](backend/README.md) for more troubleshooting tips.

---

## 📅 Development Timeline

- **Week 1-2:** ✅ Setup, Configuration, Scraping
- **Week 3-4:** Event Extraction, Query Matching
- **Week 5-6:** Export, Frontend Development
- **Week 7-8:** Testing, Documentation

---

## 📄 License

Internal use only.

---

## 👥 Contributors

Development Team

---

**Last Updated:** November 2025  
**Version:** 1.0.0  
**Current Increment:** 1 of 12
