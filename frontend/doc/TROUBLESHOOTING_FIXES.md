# Troubleshooting: Flickering Screen & Network Errors

**Date**: December 2, 2025  
**Issues**: Screen flickering in Chrome, "Network Error" on search with Bad Request (400)

---

## Issue 1: Screen Flickering in Chrome

### Root Cause
React Strict Mode causes double-rendering in development, which can cause flickering with certain UI libraries like Material-UI.

### Solution Options

#### Option A: Disable React Strict Mode (Quick Fix)

Edit `src/main.tsx`:

**Before:**
```tsx
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**After:**
```tsx
ReactDOM.createRoot(document.getElementById('root')!).render(
  <App />
)
```

**Pros**: Immediate fix for flickering  
**Cons**: Loses strict mode warnings (only affects development)

#### Option B: Fix State Management (Recommended)

The flickering may be caused by unnecessary re-renders. Keep Strict Mode but optimize the component.

---

## Issue 2: Network Error - Bad Request (400)

### Root Causes

1. **API URL mismatch** - Frontend and backend not aligned
2. **Request body format** - Data not matching backend expectations
3. **CORS issues** - Backend not allowing frontend origin
4. **Backend not running** - API server offline

### Diagnostic Steps

#### Step 1: Verify Backend is Running

```powershell
# Check if backend is running
curl http://127.0.0.1:8000/api/v1/health
```

**Expected Response:**
```json
{"status":"healthy","timestamp":"...","version":"1.0.0"}
```

**If fails**: Start backend server
```powershell
cd ..\backend
uvicorn app.main:app --reload
```

#### Step 2: Check API Endpoint Format

The frontend sends:
```json
{
  "phrase": "AI conference",
  "location": "",
  "event_type": null,
  "date_from": "",
  "date_to": ""
}
```

Backend expects (Pydantic model):
```python
class SearchRequest(BaseModel):
    phrase: str
    location: Optional[str] = None
    event_type: Optional[EventType] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
```

**Problem**: Empty strings (`""`) should be `null`/`undefined`

#### Step 3: Test API Directly

```powershell
# Test the API endpoint directly
$body = @{
    phrase = "AI conference"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/search" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

---

## Fixes

### Fix 1: Update API Service (Handle Empty Strings)

Edit `src/services/api.ts`:

```typescript
/**
 * Execute a search with the given query parameters
 */
async searchEvents(query: SearchQuery): Promise<SearchResponse> {
  // Clean the query - remove empty strings and undefined values
  const cleanedQuery = {
    phrase: query.phrase,
    ...(query.location && { location: query.location }),
    ...(query.event_type && { event_type: query.event_type }),
    ...(query.date_from && { date_from: query.date_from }),
    ...(query.date_to && { date_to: query.date_to }),
  };

  const response = await this.client.post<SearchResponse>('/api/v1/search', cleanedQuery);
  return response.data;
}
```

### Fix 2: Update SearchForm to Not Send Empty Strings

Edit `src/components/SearchForm.tsx` - Update the `handleSubmit` function:

```tsx
const handleSubmit = async (event: React.FormEvent) => {
  event.preventDefault();
  setError(null);

  // Validation
  if (!formData.phrase.trim()) {
    setError('Please enter a search phrase');
    return;
  }

  // Date validation
  if (formData.date_from && formData.date_to) {
    const fromDate = new Date(formData.date_from);
    const toDate = new Date(formData.date_to);
    if (fromDate > toDate) {
      setError('Start date must be before end date');
      return;
    }
  }

  try {
    setLoading(true);
    if (onSearchStart) {
      onSearchStart();
    }

    // Import API service dynamically
    const { apiService } = await import('../services/api');
    
    // Clean the query - only send non-empty values
    const cleanQuery: SearchQuery = {
      phrase: formData.phrase.trim(),
      ...(formData.location?.trim() && { location: formData.location.trim() }),
      ...(formData.event_type && { event_type: formData.event_type }),
      ...(formData.date_from && { date_from: formData.date_from }),
      ...(formData.date_to && { date_to: formData.date_to }),
    };
    
    const results = await apiService.searchEvents(cleanQuery);
    onSearchComplete(results);
  } catch (err: any) {
    console.error('Search error:', err);
    
    // Better error handling
    let errorMessage = 'An error occurred while searching. Please try again.';
    
    if (err.response) {
      // Backend returned an error
      errorMessage = `Server error: ${err.response.data?.detail || err.response.statusText}`;
    } else if (err.request) {
      // Request made but no response
      errorMessage = 'Cannot connect to server. Please ensure the backend is running on http://127.0.0.1:8000';
    } else {
      // Something else happened
      errorMessage = err.message || errorMessage;
    }
    
    setError(errorMessage);
  } finally {
    setLoading(false);
  }
};
```

### Fix 3: Verify CORS Configuration

Backend `app/main.py` should have:

```python
from fastapi.middleware.cors import CORSMiddleware

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

### Fix 4: Update API Base URL (If Needed)

If backend is on `127.0.0.1:8000` but frontend is calling `localhost:8000`:

Edit `src/services/api.ts`:

```typescript
constructor(baseURL: string = 'http://127.0.0.1:8000') {
  // Changed from localhost to 127.0.0.1 for consistency
  this.client = axios.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 120000,
  });
}
```

---

## Step-by-Step Application of Fixes

### Step 1: Fix React Strict Mode (Flickering)

```powershell
# Edit src/main.tsx
# Remove <React.StrictMode> wrapper
```

### Step 2: Fix API Service

```powershell
# Edit src/services/api.ts
# Add the cleanedQuery logic to searchEvents method
```

### Step 3: Fix SearchForm

```powershell
# Edit src/components/SearchForm.tsx
# Update handleSubmit with better error handling
```

### Step 4: Restart Frontend

```powershell
# Stop current server (Ctrl+C)
# Restart
npm run dev
```

### Step 5: Verify Backend

```powershell
# In separate terminal
cd ..\backend
uvicorn app.main:app --reload
```

### Step 6: Test

1. Open http://localhost:5173
2. Enter search: "AI conference"
3. Click Search
4. Check browser console (F12) for errors

---

## Verification Checklist

- [ ] Backend running on http://127.0.0.1:8000
- [ ] Backend health check passes: `curl http://127.0.0.1:8000/api/v1/health`
- [ ] Frontend running on http://localhost:5173
- [ ] No flickering in Chrome
- [ ] Search form accepts input
- [ ] Search returns results (not network error)
- [ ] No CORS errors in console
- [ ] No 400 Bad Request errors

---

## Common Error Messages & Solutions

### "Network Error"
**Cause**: Backend not running or wrong URL  
**Fix**: Start backend, verify URL in `api.ts`

### "Bad Request (400)"
**Cause**: Invalid request format (empty strings instead of null)  
**Fix**: Apply Fix 1 and Fix 2 above

### "CORS Error"
**Cause**: Backend doesn't allow frontend origin  
**Fix**: Update backend CORS middleware

### "Request timeout"
**Cause**: Search taking too long (>2 minutes)  
**Fix**: This is expected for large searches, increase timeout or optimize backend

---

## Debug Mode

### Enable Detailed Logging

Add to `src/services/api.ts`:

```typescript
async searchEvents(query: SearchQuery): Promise<SearchResponse> {
  console.log('Sending search request:', query);
  
  const cleanedQuery = {
    phrase: query.phrase,
    ...(query.location && { location: query.location }),
    ...(query.event_type && { event_type: query.event_type }),
    ...(query.date_from && { date_from: query.date_from }),
    ...(query.date_to && { date_to: query.date_to }),
  };
  
  console.log('Cleaned query:', cleanedQuery);
  
  try {
    const response = await this.client.post<SearchResponse>('/api/v1/search', cleanedQuery);
    console.log('Search response:', response.data);
    return response.data;
  } catch (error) {
    console.error('API Error Details:', error);
    throw error;
  }
}
```

### Check Browser Network Tab

1. Open DevTools (F12)
2. Go to Network tab
3. Perform search
4. Click on the `/api/v1/search` request
5. Check:
   - **Request Headers**: Content-Type, Origin
   - **Request Payload**: The JSON being sent
   - **Response**: Status code, error message

---

## Quick Test Script

```powershell
# Save as test-api.ps1

Write-Host "Testing Backend API..." -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health"
    Write-Host "✓ Backend is healthy" -ForegroundColor Green
    Write-Host $health
} catch {
    Write-Host "✗ Backend is not responding" -ForegroundColor Red
    exit 1
}

# Test 2: Search API
Write-Host "`n2. Testing Search API..." -ForegroundColor Yellow
$body = @{
    phrase = "AI"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/search" `
        -Method POST `
        -Body $body `
        -ContentType "application/json"
    Write-Host "✓ Search API working" -ForegroundColor Green
    Write-Host "Events found: $($result.total_matched)"
} catch {
    Write-Host "✗ Search API failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

Write-Host "`n✓ All tests passed!" -ForegroundColor Green
```

Run with:
```powershell
.\test-api.ps1
```

---

## Expected Behavior After Fixes

1. **No flickering** in Chrome browser
2. **Search works** with simple queries like "AI"
3. **Results display** in event cards
4. **Error messages** are clear and helpful
5. **Loading state** shows during search
6. **No console errors** in browser

---

## If Issues Persist

### Collect Diagnostic Info

1. **Frontend Console Errors** (F12 → Console)
2. **Network Requests** (F12 → Network → Search request)
3. **Backend Logs** (Terminal where uvicorn is running)
4. **Browser**: Chrome version
5. **Node.js Version**: `node --version`
6. **npm Version**: `npm --version`

### Contact Points

- Check `doc/REVIEW_INCREMENT9.md` for implementation details
- Check `test/TESTING_GUIDE.md` for comprehensive testing
- Backend documentation: `../backend/README.md`

---

**Status**: Ready to apply fixes  
**Estimated Time**: 10-15 minutes  
**Difficulty**: Medium

Apply fixes in order and test after each step!
