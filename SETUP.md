# ATICAS - Quick Setup Guide

## Automated Threat Intelligence Collection and Analysis System

---

## Prerequisites

- ✅ Python 3.10+ installed
- ✅ Ollama installed and running
- ✅ 8GB+ RAM (16GB recommended)

---

## Quick Start

### 1. Install Ollama

**Windows:**
Download from: https://ollama.ai/download

**Verify Installation:**
```cmd
ollama list
```

**Pull a Model (if needed):**
```cmd
# For 16GB+ RAM (Recommended)
ollama pull llama3.1:8b

# For 8-12GB RAM
ollama pull llama3.2:3b

# For 4-8GB RAM
ollama pull gemma3:1b

# For 4-8GB RAM
ollama pull qwen2.5:3b
```

**Check Ollama is Running:**
```cmd
curl http://localhost:11434
```
Should return: `Ollama is running`

---

### 2. Setup Python Environment

```cmd
# Navigate to project directory
cd c:\Anu\APT\apt\defender\scraping\code\backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model (will be needed in Increment 4)
# Note: May have compatibility issues with Python 3.13, can skip for now
python -m spacy download en_core_web_sm

#If there are issues with spaCy installation -
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

---

### 3. Configure Environment

```cmd
# Navigate to project root
cd c:\Anu\APT\apt\defender\scraping\code

# Copy example environment file (if not already exists)
copy .env.example .env

# Edit .env and set your preferred model
notepad .env
```

**Important:** The `.env` file should be in the **project root** directory:  
`c:\Anu\APT\apt\defender\scraping\code\.env`

**Recommended `.env` settings:**
```ini
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

API_HOST=0.0.0.0
API_PORT=8000
```

---

### 4. Start the Server

```cmd
# Make sure you're in the backend directory
cd c:\Anu\APT\apt\defender\scraping\code\backend

# Activate virtual environment (if not already)
..\venv\Scripts\activate

# Start the server
python -m uvicorn app.main:app --reload
```

**Server will start on:** http://localhost:8000

---

## Verify Installation

### Option 1: Browser
Open in your browser:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health
- **Ollama Status:** http://localhost:8000/api/v1/ollama/status

### Option 2: Command Line
```cmd
# Health check
curl http://localhost:8000/api/v1/health

# Ollama status
curl http://localhost:8000/api/v1/ollama/status

# Test generation (takes 5-15 seconds)
curl http://localhost:8000/api/v1/test/ollama
```

### Option 3: PowerShell
```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/health | Select-Object -Expand Content
```

---

## Expected Responses

**Health Check:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-01T...",
  "version": "1.0.0"
}
```

**Ollama Status:**
```json
{
  "status": "connected",
  "model": "llama3.1:8b",
  "base_url": "http://localhost:11434",
  "timestamp": "2025-12-01T..."
}
```

---

## Troubleshooting

### Issue: Ollama not connected
**Solution:**
```cmd
# Check if Ollama is running
curl http://localhost:11434

# List installed models
ollama list

# Test Ollama directly
ollama run llama3.1:8b "Hello"
```

### Issue: Port 8000 already in use
**Solution:**
```cmd
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process or change port in .env
API_PORT=8001
```

### Issue: Python package errors
**Solution:**
```cmd
# Reinstall packages
pip install --force-reinstall fastapi uvicorn pydantic ollama

# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

### Issue: spaCy download fails (Python 3.13 compatibility)
**Problem:** `ModuleNotFoundError: No module named 'srsly.ujson.ujson'`

**Solution 1 - Reinstall with compatible versions:**
```cmd
# Uninstall problematic packages
pip uninstall -y spacy thinc srsly

# Upgrade NumPy to 2.x (Python 3.13 compatible)
pip install --upgrade numpy

# Reinstall spaCy (will get latest compatible versions)
pip install spacy --no-cache-dir

# Download language model
python -m spacy download en_core_web_sm
```

**Solution 2 - Use main .venv instead of backend/venv:**
```cmd
# Use the main virtual environment at code root
cd c:\Anu\APT\apt\defender\scraping\code

# Install in main .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

# Download spaCy model
.venv\Scripts\python.exe -m spacy download en_core_web_sm

# Run server with main .venv
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

**Solution 3 - Skip spaCy for now (Recommended for Increment 1):**
```cmd
# spaCy is only needed for Increment 4 (NLP Entity Extraction)
# You can proceed with Increments 1-3 without it

# Just install core packages:
pip install fastapi uvicorn pydantic pydantic-settings ollama loguru python-dotenv
```

---

## Project Structure

```
c:\Anu\APT\apt\defender\scraping\code\
├── .env                    # Configuration (create from .env.example)
├── .venv\                  # Virtual environment
├── backend\
│   ├── app\
│   │   ├── main.py        # FastAPI application
│   │   ├── config.py      # Configuration management
│   │   ├── services\
│   │   │   └── ollama_service.py  # Ollama client
│   │   └── utils\
│   │       └── logger.py  # Logging setup
│   ├── requirements.txt   # Python dependencies
│   └── tests\             # Test files
├── config\                # Configuration files
├── doc\                   # Documentation
└── logs\                  # Application logs
```

---

## Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/api/v1/health` | GET | Health check |
| `/api/v1/ollama/status` | GET | Ollama connection status |
| `/api/v1/test/ollama` | GET | Test LLM generation |
| `/docs` | GET | Interactive API documentation (Swagger UI) |
| `/redoc` | GET | Alternative API documentation (ReDoc) |

---

## Development

### Run Tests
```cmd
cd backend
pytest tests/ -v
```

### View Logs
```cmd
type logs\app.log
```

### Stop Server
Press `CTRL+C` in the terminal running the server

---

## Next Steps

Once the server is running successfully:

1. ✅ **Increment 1 Complete:** Basic setup with Ollama integration
2. ➡️ **Increment 2:** Configuration & Data Models
3. ➡️ **Increment 3:** Web Scraping Engine
4. ➡️ **Increment 4:** NLP Entity Extraction

See `doc/ImplementationPlan.md` for detailed incremental development plan.

---

## Quick Commands Reference

```cmd
# Start server
cd c:\Anu\APT\apt\defender\scraping\code\backend
..\venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Check Ollama
ollama list
curl http://localhost:11434

# Test API
curl http://localhost:8000/api/v1/health

# View documentation
start http://localhost:8000/docs
```

---

## Support

- **Implementation Plan:** `doc/ImplementationPlan.md`
- **Requirements:** `doc/Military_Requirements_Document.md`
- **Architecture:** `doc/SimplifiedArchitectureDesign.md`

---

**Version:** 1.0  
**Last Updated:** December 1, 2025  
**Status:** Increment 1 Complete ✅
