# Event Scraper - Web Intelligence Gathering Tool

Automated web scraping tool for extracting, analyzing, and exporting event information from news sources using AI (Ollama LLMs).

---

## 🚀 Quick Start

See **[QUICKSTART.md](QUICKSTART.md)** for detailed setup instructions.

### TL;DR

1. **Install Ollama** → https://ollama.ai/download
2. **Pull a model:** `ollama pull llama3.1:8b`
3. **Install dependencies:**
   ```cmd
   cd backend
   ..\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
4. **Configure:** Edit `.env` file (set your model)
5. **Run server:**
   ```cmd
   cd backend
   ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```
6. **Access API:** http://localhost:8000/docs

---

## 📋 Features

- ✅ **Automated Web Scraping** - Extract content from multiple news sources
- ✅ **AI-Powered Analysis** - Event detection and classification using Ollama
- ✅ **Entity Extraction** - Identify people, organizations, locations, dates
- ✅ **Structured Export** - Export to Excel with detailed event information
- ✅ **RESTful API** - FastAPI backend with interactive documentation
- 🔄 **React Frontend** - Coming soon

---

## 📁 Project Structure

```
code/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── config.py        # Configuration management
│   │   ├── services/        # Ollama, scraping, NLP services
│   │   └── utils/           # Utilities and logging
│   └── requirements.txt     # Python dependencies
├── doc/                     # Documentation
├── .env                     # Environment configuration
└── QUICKSTART.md           # Setup guide
```

---

## 🛠️ Technology Stack

- **Backend:** Python 3.13, FastAPI, Uvicorn
- **AI/LLM:** Ollama (llama3.1:8b, gpt-oss:20b, gemma3:1b)
- **NLP:** spaCy (entity extraction)
- **Web Scraping:** httpx, BeautifulSoup4
- **Export:** openpyxl (Excel)
- **Frontend:** React (planned)

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Setup and running guide
- **[doc/ImplementationPlan.md](doc/ImplementationPlan.md)** - Development roadmap
- **[doc/WebScraperRequirementDocument.md](doc/WebScraperRequirementDocument.md)** - Requirements specification

---

## 🎯 Current Status

**Phase:** Increment 1 Complete ✅

- ✅ Project setup and structure
- ✅ Ollama integration
- ✅ FastAPI endpoints (health, status, test)
- ✅ Configuration management
- ✅ Logging system

**Next:** Increment 2 - Configuration & Data Models

---

## 📡 API Endpoints

- `GET /` - API information
- `GET /api/v1/health` - Health check
- `GET /api/v1/ollama/status` - Ollama connection status
- `GET /api/v1/test/ollama` - Test LLM generation
- `GET /docs` - Interactive API documentation

---

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
