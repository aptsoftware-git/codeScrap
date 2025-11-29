# Event Scraper - Backend Setup

## Increment 1: Project Setup & Ollama Integration ✅

This is the initial setup for the Event Scraper backend application.

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.10 or higher** installed
- ✅ **Ollama** installed natively on your machine
- ✅ **Git** (optional, for version control)

---

## Step 1: Verify Ollama Installation

### Check if Ollama is Running

```cmd
REM Windows Command Prompt
curl http://localhost:11434
```

You should see a message like "Ollama is running".

### Check Your Installed Models

```cmd
ollama list
```

You should see your `gpt-oss:20b` model listed:
```
NAME             ID              SIZE      MODIFIED
gpt-oss:20b      abc123def       12 GB     2 weeks ago
```

If you don't have any models, you can pull one:
```cmd
ollama pull llama3.1:8b
```

---

## Step 2: Create Virtual Environment

Open Command Prompt and navigate to the backend directory:

```cmd
cd c:\Anu\APT\apt\defender\scraping\code\backend
```

Create a virtual environment:

```cmd
python -m venv venv
```

Activate the virtual environment:

```cmd
REM Windows
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

---

## Step 3: Install Dependencies

With the virtual environment activated, install the required packages:

```cmd
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Ollama (LLM client)
- Loguru (logging)
- And other dependencies

**Note:** This may take a few minutes.

---

## Step 4: Download spaCy Model

Install the English language model for spaCy:

```cmd
python -m spacy download en_core_web_sm
```

---

## Step 5: Configure Environment Variables

Copy the example environment file:

```cmd
cd ..
copy .env.example .env
```

Edit the `.env` file and configure your model:

```bash
# .env
OLLAMA_MODEL=gpt-oss:20b  # Your installed model
```

**Note:** You can use any text editor (Notepad, VS Code, etc.) to edit the `.env` file.

---

## Step 6: Run the Application

Navigate back to the backend directory and run the application:

```cmd
cd backend
venv\Scripts\activate  REM If not already activated
uvicorn app.main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Step 7: Test the API

Open a **new** Command Prompt window and test the endpoints:

### Test 1: Health Check

```cmd
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-26T...",
  "version": "1.0.0"
}
```

### Test 2: Ollama Status

```cmd
curl http://localhost:8000/api/v1/ollama/status
```

Expected response:
```json
{
  "status": "connected",
  "model": "gpt-oss:20b",
  "base_url": "http://localhost:11434",
  "timestamp": "2025-11-26T..."
}
```

### Test 3: Ollama Generation Test

```cmd
curl http://localhost:8000/api/v1/test/ollama
```

This will test actual text generation with your model.

---

## Step 8: Access API Documentation

Open your web browser and visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can interact with the API directly from the Swagger UI.

---

## Step 9: Run Tests (Optional)

With the virtual environment activated:

```cmd
pytest tests/ -v
```

**Note:** Some tests require Ollama to be running.

---

## Troubleshooting

### Issue: "Ollama client not initialized"

**Solution:**
1. Check if Ollama is running: `curl http://localhost:11434`
2. Verify the model exists: `ollama list`
3. Check the `.env` file has correct `OLLAMA_MODEL` value

### Issue: "Import errors" when running the app

**Solution:**
1. Make sure virtual environment is activated (you should see `(venv)` in prompt)
2. Re-install dependencies: `pip install -r requirements.txt`

### Issue: "Port 8000 already in use"

**Solution:**
Run on a different port:
```cmd
uvicorn app.main:app --reload --port 8001
```

### Issue: Model is too slow

**Solution:**
1. If you have an NVIDIA GPU, Ollama will automatically use it
2. Check GPU usage: `nvidia-smi`
3. Alternatively, use a smaller model in `.env`:
   ```
   OLLAMA_MODEL=llama3.1:8b
   ```

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── services/
│   │   ├── __init__.py
│   │   └── ollama_service.py  # Ollama client wrapper
│   └── utils/
│       ├── __init__.py
│       └── logger.py        # Logging configuration
├── tests/
│   ├── __init__.py
│   └── test_ollama_service.py
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Next Steps

Once Increment 1 is complete and all tests pass:

✅ You have a working FastAPI application  
✅ Ollama integration is functional  
✅ API endpoints are responding  
✅ Tests are passing  

**Ready for Increment 2:** Configuration & Data Models

---

## Useful Commands Reference

```cmd
REM Activate virtual environment
venv\Scripts\activate

REM Deactivate virtual environment
deactivate

REM Run application
uvicorn app.main:app --reload

REM Run application on different port
uvicorn app.main:app --reload --port 8001

REM Run tests
pytest tests/ -v

REM Run tests with coverage
pytest tests/ -v --cov=app

REM Check Ollama models
ollama list

REM Check if Ollama is running
curl http://localhost:11434
```

---

## Getting Help

If you encounter issues:

1. Check the logs in `logs/app.log`
2. Verify Ollama is running: `curl http://localhost:11434`
3. Check your model is installed: `ollama list`
4. Ensure virtual environment is activated
5. Review the troubleshooting section above

---

**Last Updated:** November 2025  
**Version:** 1.0.0  
**Status:** Increment 1 Complete ✅
