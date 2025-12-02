# Backend CORS Fix - OPTIONS 400 Bad Request

**Date**: December 2, 2025  
**Error**: `OPTIONS /api/v1/search HTTP/1.1" 400 Bad Request`  
**Cause**: CORS preflight requests not handled properly

---

## Problem

The backend is rejecting CORS preflight (OPTIONS) requests with 400 Bad Request.

### What's Happening

1. Frontend (http://localhost:5173) sends OPTIONS request to backend (http://127.0.0.1:8000)
2. Backend rejects it with 400 Bad Request
3. Browser blocks the actual POST request
4. Frontend shows "Network Error"

### Why It Happens

- CORS middleware not configured correctly
- OPTIONS method not allowed
- Missing CORS headers

---

## Solution: Fix Backend CORS Configuration

### File: `backend/app/main.py`

**Add or update the CORS middleware:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Event Scraper & Analyzer API",
    version="1.0.0",
    description="API for scraping and analyzing events from news sources"
)

# CORS Configuration - MUST be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Frontend dev server
        "http://127.0.0.1:5173",      # Alternative localhost
        "http://localhost:3000",      # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly include OPTIONS
    allow_headers=["*"],              # Allow all headers
    expose_headers=["*"],             # Expose all headers
    max_age=3600,                     # Cache preflight for 1 hour
)

# ... rest of your routes
```

---

## Key Points

### 1. Allow OPTIONS Method
```python
allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
# Explicitly include OPTIONS for preflight requests
```

### 2. Allow All Headers
```python
allow_headers=["*"]
# Accept any headers from frontend
```

### 3. Include Both localhost and 127.0.0.1
```python
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
# Both are needed for proper CORS
```

### 4. Position Matters
```python
# CORS middleware MUST be added BEFORE routes
app.add_middleware(CORSMiddleware, ...)

@app.get("/")  # Routes come AFTER middleware
```

---

## Complete Backend Example

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Event Scraper & Analyzer API",
    version="1.0.0"
)

# ===== CORS CONFIGURATION (FIRST) =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Or list explicitly: ["GET", "POST", "OPTIONS"]
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# ===== ROUTES (AFTER MIDDLEWARE) =====
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/search")
async def search_events(request: SearchRequest):
    # Your search logic
    pass
```

---

## How to Apply the Fix

### Step 1: Stop Backend Server
```powershell
# In backend terminal, press Ctrl+C
```

### Step 2: Edit main.py

Navigate to `backend/app/main.py` and update the CORS middleware as shown above.

### Step 3: Restart Backend
```powershell
cd backend
uvicorn app.main:app --reload
```

### Step 4: Test

The backend should now show:
```
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

### Step 5: Verify CORS

Try search from frontend - should now work without OPTIONS errors.

---

## Verification

### Check Backend Logs

**Before Fix:**
```
INFO: 127.0.0.1:51750 - "OPTIONS /api/v1/search HTTP/1.1" 400 Bad Request ❌
```

**After Fix:**
```
INFO: 127.0.0.1:51750 - "OPTIONS /api/v1/search HTTP/1.1" 200 OK ✅
INFO: 127.0.0.1:51750 - "POST /api/v1/search HTTP/1.1" 200 OK ✅
```

### Check Browser Console

**Before:**
```
CORS error: Access to XMLHttpRequest blocked
Network Error
```

**After:**
```
✅ No CORS errors
✅ Search successful
```

---

## Alternative: Minimal CORS Fix

If you just want a quick fix for development:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins (dev only!)
    allow_credentials=True,
    allow_methods=["*"],          # Allow all methods
    allow_headers=["*"],          # Allow all headers
)
```

⚠️ **Warning**: `allow_origins=["*"]` is NOT secure for production!

---

## Common CORS Issues

### Issue 1: OPTIONS Still Failing

**Check**: Is middleware added BEFORE routes?
```python
# ❌ WRONG ORDER
@app.get("/")
def root():
    pass

app.add_middleware(CORSMiddleware, ...)  # Too late!

# ✅ CORRECT ORDER
app.add_middleware(CORSMiddleware, ...)  # First

@app.get("/")
def root():
    pass
```

### Issue 2: Specific Origin Not Working

**Try**: Add both localhost and 127.0.0.1
```python
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Add both!
]
```

### Issue 3: Still Getting 400

**Check**: Are you using the right HTTP method?
```python
allow_methods=["GET", "POST", "OPTIONS"]
# Make sure OPTIONS is included!
```

---

## Testing the Fix

### Test 1: Health Endpoint
```powershell
curl http://127.0.0.1:8000/api/v1/health
```
Expected: `{"status":"healthy",...}`

### Test 2: OPTIONS Request
```powershell
curl -X OPTIONS http://127.0.0.1:8000/api/v1/search -I
```
Expected: `HTTP/1.1 200 OK` with CORS headers

### Test 3: Frontend Search
1. Open http://localhost:5173
2. Search for "AI"
3. Check browser console (F12)
4. Should see no CORS errors

---

## Production Configuration

For production, use specific origins:

```python
import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
        "http://localhost:5173",
        "https://your-production-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)
```

Then use environment variable:
```bash
export ALLOWED_ORIGINS="https://your-domain.com,https://www.your-domain.com"
```

---

## Debugging CORS

### Enable CORS Logging

Add this to see CORS headers:

```python
@app.middleware("http")
async def log_cors(request, call_next):
    print(f"Request: {request.method} {request.url}")
    print(f"Origin: {request.headers.get('origin')}")
    
    response = await call_next(request)
    
    print(f"Response Status: {response.status_code}")
    print(f"CORS Headers: {response.headers.get('access-control-allow-origin')}")
    
    return response
```

### Check CORS Headers

In browser (F12 → Network → Request):
- **Request Headers**: Should include `Origin: http://localhost:5173`
- **Response Headers**: Should include `Access-Control-Allow-Origin: http://localhost:5173`

---

## Summary

### The Fix
```python
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
```

### Where to Add
- **File**: `backend/app/main.py`
- **Position**: BEFORE route definitions
- **After**: FastAPI app creation

### After Applying
1. Restart backend: `uvicorn app.main:app --reload`
2. Test frontend: http://localhost:5173
3. Verify: No OPTIONS 400 errors in backend logs
4. Confirm: Search works from frontend

---

## Quick Fix Script

Save as `fix-cors.py`:

```python
# Check if CORS is configured correctly

import sys
import re

def check_cors(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for CORSMiddleware
    if 'CORSMiddleware' not in content:
        print("❌ CORSMiddleware not found!")
        return False
    
    # Check for allow_methods
    if 'allow_methods' not in content:
        print("⚠️  allow_methods not specified")
    elif '"*"' in content or "'*'" in content:
        print("✅ allow_methods includes all methods")
    else:
        print("ℹ️  Check if allow_methods includes OPTIONS")
    
    # Check for allow_origins
    if 'allow_origins' not in content:
        print("❌ allow_origins not found!")
        return False
    else:
        print("✅ allow_origins configured")
    
    print("\n✅ CORS appears to be configured")
    return True

if __name__ == "__main__":
    check_cors("backend/app/main.py")
```

Run with:
```powershell
python fix-cors.py
```

---

**Status**: Ready to apply  
**Difficulty**: Easy  
**Time**: 5 minutes

Apply the CORS fix to `backend/app/main.py` and restart the backend!
