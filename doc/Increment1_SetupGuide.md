# Increment 1 Setup Guide - Step by Step

## ✅ Increment 1: Project Setup & Ollama Integration

**Time Required:** 30-45 minutes  
**Status:** Implementation Complete - Ready for Manual Setup

---

## 🎯 What Has Been Created

I've created the complete project structure with:

- ✅ Backend application with FastAPI
- ✅ Ollama client integration
- ✅ Configuration management
- ✅ Logging system
- ✅ Basic API endpoints
- ✅ Test suite
- ✅ Documentation

---

## 📋 Manual Steps Required

### Step 1: Verify Ollama is Running ✋ **ACTION REQUIRED**

Open Command Prompt and run:

```cmd
curl http://localhost:11434
```

**Expected Output:** `Ollama is running`

**If it fails:**
- Start Ollama from the Start menu (Windows)
- Or reinstall from https://ollama.ai/download

---

### Step 2: Check Your Model ✋ **ACTION REQUIRED**

```cmd
ollama list
```

**Expected Output:** You should see `gemma3:1b` or another small model in the list

**Important:** If you see `gpt-oss:20b` (13 GB), it's too large for systems with <10 GiB RAM.
Use `gemma3:1b` (815 MB) instead - it's already installed!

```
NAME             ID              SIZE      MODIFIED
gpt-oss:20b      abc123def       12 GB     2 weeks ago
```

✅ **You're good to go with your existing model!**

---

### Step 3: Create Virtual Environment ✋ **ACTION REQUIRED**

Open Command Prompt and navigate to the backend directory:

```cmd
cd c:\Anu\APT\apt\defender\scraping\code\backend
```

Create virtual environment:

```cmd
python -m venv venv
```

**Expected Output:** Creates a `venv` folder in the backend directory

---

### Step 4: Activate Virtual Environment ✋ **ACTION REQUIRED**

```cmd
venv\Scripts\activate
```

**Expected Output:** Your prompt should change to show `(venv)` at the beginning:

```
(venv) C:\Anu\APT\apt\defender\scraping\code\backend>
```

---

### Step 5: Install Python Dependencies ✋ **ACTION REQUIRED**

**This will take 5-10 minutes**

```cmd
pip install -r requirements.txt
```

**Expected Output:** 
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

**Note:** You may see some warnings - these are normal.

---

### Step 6: Download spaCy Language Model ✋ **ACTION REQUIRED**

```cmd
python -m spacy download en_core_web_sm
```

**Expected Output:**
```
Successfully installed en_core_web_sm-3.7.x
```

---

### Step 7: Create .env File ✋ **ACTION REQUIRED**

Navigate back to the project root:

```cmd
cd ..
```

Copy the example environment file:

```cmd
copy .env.example .env
```

**Edit the .env file** (use Notepad or any text editor):

```cmd
notepad .env
```

Make sure it contains:

```bash
OLLAMA_MODEL=gpt-oss:20b
```

Save and close the file.

---

### Step 8: Start the Backend ✋ **ACTION REQUIRED**

Navigate to backend directory:

```cmd
cd backend
```

Make sure virtual environment is activated (you should see `(venv)` in prompt):

```cmd
venv\Scripts\activate
```

Run the application:

```cmd
uvicorn app.main:app --reload
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['C:\\Anu\\APT\\...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
2025-11-26 10:30:00 | INFO     | app.main:startup_event:35 - Starting Event Scraper API...
2025-11-26 10:30:00 | INFO     | app.main:startup_event:36 - Ollama URL: http://localhost:11434
2025-11-26 10:30:00 | INFO     | app.main:startup_event:37 - Ollama Model: gpt-oss:20b
2025-11-26 10:30:01 | INFO     | app.services.ollama_service:__init__:19 - OllamaClient initialized with base_url=http://localhost:11434, model=gpt-oss:20b
INFO:     Application startup complete.
```

**Leave this terminal open** - the application is now running!

---

### Step 9: Test the API ✋ **ACTION REQUIRED**

**Open a NEW Command Prompt window** (keep the first one running)

#### Test 1: Health Check

```cmd
curl http://localhost:8000/api/v1/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-26T10:30:00.123456",
  "version": "1.0.0"
}
```

✅ **If you see this, your API is working!**

---

#### Test 2: Ollama Status

```cmd
curl http://localhost:8000/api/v1/ollama/status
```

**Expected Output:**
```json
{
  "status": "connected",
  "model": "gpt-oss:20b",
  "base_url": "http://localhost:11434",
  "timestamp": "2025-11-26T10:30:00.123456"
}
```

✅ **If status is "connected", Ollama integration is working!**

---

#### Test 3: Test Ollama Generation

```cmd
curl http://localhost:8000/api/v1/test/ollama
```

**Expected Output:** (This will take 10-20 seconds with gpt-oss:20b)
```json
{
  "status": "success",
  "model": "gpt-oss:20b",
  "prompt": "Say 'Hello, World!' in a friendly way.",
  "response": "Hello, World! It's wonderful to connect with you today...",
  "timestamp": "2025-11-26T10:30:15.123456"
}
```

✅ **If you see a response, your LLM is working perfectly!**

---

### Step 10: Access API Documentation ✋ **ACTION REQUIRED**

Open your web browser and visit:

**Swagger UI:** http://localhost:8000/docs

You should see an interactive API documentation page where you can:
- See all available endpoints
- Test endpoints directly from the browser
- View request/response schemas

---

### Step 11: Run Tests (Optional) ✋ **ACTION REQUIRED**

In the second terminal (NOT the one running uvicorn):

```cmd
cd c:\Anu\APT\apt\defender\scraping\code\backend
venv\Scripts\activate
pytest tests/ -v
```

**Expected Output:**
```
tests/test_ollama_service.py::test_ollama_client_initialization PASSED
tests/test_ollama_service.py::test_extract_json PASSED
...
======================== X passed in Y.YYs ========================
```

---

## ✅ Success Criteria Checklist

After completing all steps, verify:

- [ ] Ollama is running (`curl http://localhost:11434` works)
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] Application starts without errors
- [ ] Health check endpoint returns "healthy"
- [ ] Ollama status endpoint returns "connected"
- [ ] Test generation endpoint produces a response
- [ ] API documentation is accessible at /docs
- [ ] Tests pass (if you ran them)

---

## 🎉 Increment 1 Complete!

If all tests pass, **congratulations!** You have successfully completed Increment 1.

**What You've Achieved:**
- ✅ Working FastAPI application
- ✅ Ollama integration with your gpt-oss:20b model
- ✅ API endpoints responding correctly
- ✅ Logging system configured
- ✅ Test suite in place

**Next Increment:** Configuration & Data Models (Increment 2)

---

## 🐛 Common Issues and Solutions

### Issue: "curl: command not found"

**Solution:** Use PowerShell instead:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/v1/health
```

Or install Git for Windows which includes curl.

---

### Issue: "Ollama client not initialized"

**Solution:**
1. Check Ollama is running: `curl http://localhost:11434`
2. If not, start Ollama from Start menu
3. Verify model exists: `ollama list`
4. Restart the FastAPI application

---

### Issue: "Port 8000 already in use"

**Solution:** Use a different port:
```cmd
uvicorn app.main:app --reload --port 8001
```

Then test with: `curl http://localhost:8001/api/v1/health`

---

### Issue: Import errors or module not found

**Solution:**
1. Verify virtual environment is activated (see `(venv)` in prompt)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Make sure you're in the backend directory

---

### Issue: "No module named 'app'"

**Solution:** Make sure you're running uvicorn from the `backend` directory:
```cmd
cd c:\Anu\APT\apt\defender\scraping\code\backend
uvicorn app.main:app --reload
```

---

## 📞 Getting Help

If you encounter issues:

1. **Check the logs:** Look at `logs/app.log` in the project directory
2. **Verify Ollama:** `ollama list` should show your model
3. **Check Python version:** `python --version` (should be 3.10+)
4. **Virtual environment:** Make sure it's activated (see `(venv)`)

---

## 🔄 Stopping the Application

To stop the backend:

1. Go to the terminal running `uvicorn`
2. Press `CTRL+C`
3. Wait for graceful shutdown

To deactivate virtual environment:
```cmd
deactivate
```

---

## 🚀 Next Steps

Once Increment 1 is verified working:

1. Read through the code in `backend/app/main.py`
2. Familiarize yourself with the project structure
3. Review `doc/ImplementationPlan.md` for Increment 2
4. Get ready to implement Configuration & Data Models

---

**Document Created:** November 2025  
**Increment:** 1 of 12  
**Status:** Complete ✅
