# 🔧 Quick Fix: OPTIONS 400 Bad Request

**Error**: `OPTIONS /api/v1/search HTTP/1.1" 400 Bad Request`  
**Cause**: Backend CORS not configured for preflight requests  
**Solution**: Update backend CORS middleware

---

## ⚡ Quick Fix (5 minutes)

### Step 1: Open Backend File
```powershell
# Navigate to backend
cd ..\backend

# Open main.py in editor
code app\main.py
```

### Step 2: Find or Add CORS Middleware

Look for this section near the top of `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(...)
```

### Step 3: Update CORS Configuration

**Replace or add this code IMMEDIATELY AFTER `app = FastAPI(...)`:**

```python
# CORS Configuration - Add this BEFORE any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # This allows OPTIONS requests
    allow_headers=["*"],
    expose_headers=["*"],
)
```

### Step 4: Restart Backend

```powershell
# Stop backend (Ctrl+C)
# Restart
uvicorn app.main:app --reload
```

### Step 5: Test

Open frontend (http://localhost:5173) and try searching for "AI"

---

## ✅ What You Should See

### Backend Logs (BEFORE Fix)
```
❌ INFO: 127.0.0.1:51750 - "OPTIONS /api/v1/search HTTP/1.1" 400 Bad Request
```

### Backend Logs (AFTER Fix)
```
✅ INFO: 127.0.0.1:51750 - "OPTIONS /api/v1/search HTTP/1.1" 200 OK
✅ INFO: 127.0.0.1:51750 - "POST /api/v1/search HTTP/1.1" 200 OK
```

---

## 📋 Complete Example

If you need to see the full structure:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Event Scraper & Analyzer API",
    version="1.0.0"
)

# ===== ADD CORS HERE (CRITICAL!) =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Your routes go below =====
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

# ... rest of your code
```

---

## 🎯 Key Points

1. **Position Matters**: CORS middleware MUST be added BEFORE routes
2. **Allow OPTIONS**: Use `allow_methods=["*"]` or explicitly include "OPTIONS"
3. **Both URLs**: Include both `localhost:5173` and `127.0.0.1:5173`
4. **Restart Required**: Backend must be restarted after changes

---

## 🧪 Quick Test

```powershell
# Test OPTIONS request directly
curl -X OPTIONS http://127.0.0.1:8000/api/v1/search -I

# Expected response headers should include:
# Access-Control-Allow-Origin: http://localhost:5173
# Access-Control-Allow-Methods: GET, POST, OPTIONS, ...
```

---

## 📚 Full Documentation

See `doc/BACKEND_CORS_FIX.md` for complete details and troubleshooting.

---

**Status**: Ready to apply  
**Time**: 5 minutes  
**Difficulty**: Easy ⭐

Fix the CORS configuration and your search will work! 🚀
