# Increment 1 - Quick Checklist

## Pre-Setup Verification

- [ ] Ollama is installed
- [ ] Run `ollama list` - see `llama3.1:8b` (recommended for 16GB RAM)
- [ ] Run `curl http://localhost:11434` - see "Ollama is running"
- [ ] Python 3.10+ installed - `python --version`
- [ ] **Your system:** 16GB RAM = Perfect for llama3.1:8b!

---

## Setup Steps

### 1. Create Virtual Environment
```cmd
cd c:\Anu\APT\apt\defender\scraping\code\backend
python -m venv venv
```
- [ ] `venv` folder created

### 2. Activate Virtual Environment
```cmd
venv\Scripts\activate
```
- [ ] Prompt shows `(venv)`

### 3. Install Dependencies
```cmd
pip install -r requirements.txt
```
- [ ] All packages installed successfully

### 4. Install spaCy Model
```cmd
python -m spacy download en_core_web_sm
```
- [ ] Model downloaded

### 5. Configure Environment
```cmd
cd ..
copy .env.example .env
notepad .env
```
- [ ] `.env` file created
- [ ] `OLLAMA_MODEL=llama3.1:8b` is set

### 6. Run Application
```cmd
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```
- [ ] Server starts without errors
- [ ] See "Application startup complete"

---

## Testing (In New Terminal)

### 7. Health Check
```cmd
curl http://localhost:8000/api/v1/health
```
- [ ] Returns `{"status": "healthy", ...}`

### 8. Ollama Status
```cmd
curl http://localhost:8000/api/v1/ollama/status
```
- [ ] Returns `{"status": "connected", "model": "llama3.1:8b", ...}`

### 9. Test Generation
```cmd
curl http://localhost:8000/api/v1/test/ollama
```
- [ ] Returns successful response with generated text

### 10. API Docs
- [ ] Open http://localhost:8000/docs in browser
- [ ] See Swagger UI with endpoints listed

---

## Optional: Run Tests
```cmd
cd backend
venv\Scripts\activate
pytest tests/ -v
```
- [ ] All tests pass

---

## ✅ Increment 1 Complete When:

- [ ] All checkboxes above are checked
- [ ] No errors in terminal
- [ ] All API endpoints respond correctly
- [ ] Ollama integration works

---

## Next: Increment 2

Once complete, proceed to:
- Configuration & Data Models
- See `doc/ImplementationPlan.md`

---

**Quick Reference:**

Start backend:
```cmd
cd c:\Anu\APT\apt\defender\scraping\code\backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

Stop backend: `CTRL+C`
