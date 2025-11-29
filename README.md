# Event-Focused Web Scraping, Summarization & Export Tool

A Python-based web scraping tool that extracts, summarizes, and exports event information from news sources using Ollama LLMs.

---

## 🎯 Project Status

**Current Phase:** Increment 1 - Project Setup & Ollama Integration ✅

### Completed
- ✅ Project structure created
- ✅ FastAPI backend setup
- ✅ Ollama integration with `gpt-oss:20b` model
- ✅ Basic API endpoints (health check, Ollama status)
- ✅ Configuration management
- ✅ Logging setup

### Next Steps
- 📋 Increment 2: Configuration & Data Models
- 📋 Increment 3: Web Scraping Engine
- 📋 Increment 4: NLP Entity Extraction

---

## 📁 Project Structure

```
event-scraper/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── main.py      # Application entry point
│   │   ├── config.py    # Configuration
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   ├── tests/           # Unit tests
│   └── requirements.txt
├── frontend/            # React frontend (coming in Increment 9)
├── config/              # Configuration files
├── logs/                # Application logs
├── doc/                 # Documentation
└── .env                 # Environment variables
```

---

## 🚀 Quick Start

### Prerequisites

1. **Ollama** (installed natively)
   - Download: https://ollama.ai/download
   - Verify: `ollama list` shows `gpt-oss:20b`

2. **Python 3.10+**
   - Check: `python --version`

### Setup (5 minutes)

```cmd
REM 1. Navigate to backend directory
cd backend

REM 2. Create virtual environment
python -m venv venv

REM 3. Activate virtual environment
venv\Scripts\activate

REM 4. Install dependencies
pip install -r requirements.txt

REM 5. Download spaCy model
python -m spacy download en_core_web_sm

REM 6. Configure environment
cd ..
copy .env.example .env
REM Edit .env and set OLLAMA_MODEL=gpt-oss:20b

REM 7. Run the application
cd backend
uvicorn app.main:app --reload
```

### Test

```cmd
REM In a new terminal
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/ollama/status
```

Visit http://localhost:8000/docs for interactive API documentation.

---

## 📚 Documentation

- **[Requirements](doc/WebScraperRequirementDocument.md)** - Full project requirements
- **[Architecture](doc/SimplifiedArchitectureDesign.md)** - System architecture and design
- **[Implementation Plan](doc/ImplementationPlan.md)** - 12-increment development plan
- **[Model Configuration](doc/ModelConfiguration.md)** - Ollama model selection guide
- **[Backend README](backend/README.md)** - Detailed backend setup instructions

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
