# Frontend-Backend Integration Testing Guide

## Test Environment

- **Backend**: http://127.0.0.1:8000 ✅ Running
- **Frontend**: http://localhost:5173 ✅ Running
- **Status**: Both servers operational

---

## Quick Tests

### 1. Backend Health Check ✅

```bash
curl http://127.0.0.1:8000/api/v1/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-02T...",
  "version": "1.0.0"
}
```

### 2. Check Backend API Documentation

Open in browser: http://127.0.0.1:8000/docs

This shows the FastAPI Swagger UI with all available endpoints.

---

## Integration Test Steps

### Test 1: Simple Search (Manual UI Test)

1. **Open Frontend**: http://localhost:5173
2. **Enter Search Query**:
   - Phrase: `"AI conference"`
   - Leave other fields empty
3. **Click "Search"**
4. **Expected Behavior**:
   - Loading spinner appears
   - "Searching and analyzing events..." message
   - After 30-60s: Results appear
   - Events displayed as cards
   - Summary shows: "Found X matching events from Y extracted events"

### Test 2: Search with Filters

1. **Enter Search Query**:
   - Phrase: `"cybersecurity"`
   - Location: `"San Francisco"`
   - Event Type: `"conference"`
   - Date From: `"2025-01-01"`
   - Date To: `"2025-12-31"`
2. **Click "Search"**
3. **Verify**:
   - Results match filters
   - Only conferences shown
   - Dates within range

### Test 3: Sort Functionality

1. **After search completes**:
   - Try "Sort By: Relevance" - highest scores first
   - Try "Sort By: Date" - chronological order
   - Try "Sort By: Title" - alphabetical order
2. **Verify**: Results re-order correctly

### Test 4: Excel Export

1. **After search completes**:
   - Click "Export to Excel" button
   - Button shows "Exporting..."
2. **Verify**:
   - Excel file downloads (events_*.xlsx)
   - File opens in Excel
   - Contains Events and Summary sheets
   - Data matches displayed results

---

## API Endpoint Tests (Using curl or Postman)

### Test Backend Search API Directly

```bash
# Test search endpoint
curl -X POST http://127.0.0.1:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d "{\"phrase\": \"AI conference\", \"location\": \"online\"}"
```

**Expected Response**:
```json
{
  "session_id": "uuid-here",
  "query": {
    "phrase": "AI conference",
    "location": "online"
  },
  "events": [...],
  "total_scraped": 50,
  "total_extracted": 20,
  "total_matched": 10,
  "processing_time": 45.23,
  "sources_scraped": ["source1.com", "source2.com"]
}
```

### Test Session Retrieval

```bash
# Replace SESSION_ID with actual ID from search response
curl http://127.0.0.1:8000/api/v1/search/session/SESSION_ID
```

### Test Excel Export

```bash
# Replace SESSION_ID with actual ID
curl -X POST http://127.0.0.1:8000/api/v1/export/excel \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"SESSION_ID\"}" \
  --output test_export.xlsx
```

---

## Troubleshooting

### Issue: CORS Error in Browser Console

**Symptoms**: 
```
Access to XMLHttpRequest at 'http://127.0.0.1:8000/api/v1/search' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution**: 
The backend needs CORS configuration. Check if backend has:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Connection Refused

**Symptoms**: `ERR_CONNECTION_REFUSED` or network error

**Solutions**:
1. Verify backend is running: `curl http://127.0.0.1:8000/api/v1/health`
2. Check backend logs for errors
3. Verify port 8000 is not blocked by firewall

### Issue: Search Takes Too Long

**Expected**: Search should complete in 30-60 seconds

**If longer**:
- Check backend logs for errors
- Verify Ollama is running: http://localhost:11434
- Check network connectivity to news sources
- Some sources may be slow or timing out (normal)

### Issue: No Results Found

**Possible Causes**:
1. No articles match the query
2. Articles scraped but no events extracted
3. Events extracted but relevance score too low

**Debug Steps**:
1. Check backend logs for scraping activity
2. Try broader search terms
3. Remove filters (location, event type, dates)

---

## Browser DevTools Testing

### Open Browser Console (F12)

1. **Go to Network Tab**
2. **Submit a search**
3. **Check XHR/Fetch requests**:
   - Should see POST to `/api/v1/search`
   - Check request payload
   - Check response status (200 = success)
   - View response JSON

### Monitor Console for Errors

Look for:
- ✅ No CORS errors
- ✅ No 404 errors
- ✅ No network timeouts
- ✅ Successful API responses

---

## Performance Testing

### Measure Search Performance

1. **Start search** - note timestamp
2. **Wait for results**
3. **Check processing time** in results summary
4. **Expected**: 
   - Scraping: 10-20s
   - Extraction: 20-40s
   - Matching: <1s
   - **Total**: 30-60s

### Measure UI Responsiveness

- Initial load: < 1s ✅
- Form interactions: Instant ✅
- Sorting: Instant ✅
- Export: 1-2s ✅

---

## Test Checklist

### Frontend Tests

- [ ] Page loads without errors
- [ ] Search form displays correctly
- [ ] All form fields are functional
- [ ] Required field validation works
- [ ] Date range validation works
- [ ] Submit button triggers search
- [ ] Loading state displays during search
- [ ] Error messages display correctly
- [ ] Results display after search
- [ ] Event cards show all fields
- [ ] Sorting works (3 modes)
- [ ] Export button triggers download
- [ ] Excel file downloads correctly
- [ ] Reset button clears form
- [ ] Responsive on mobile
- [ ] No console errors

### Backend Integration Tests

- [ ] Backend health check passes
- [ ] Search API endpoint works
- [ ] Session retrieval works
- [ ] Excel export works
- [ ] CORS configured correctly
- [ ] Errors handled gracefully
- [ ] Processing times acceptable
- [ ] Results match query

### End-to-End Tests

- [ ] Full search flow (form → API → results)
- [ ] Export flow (results → Excel download)
- [ ] Multiple searches in sequence
- [ ] Browser refresh preserves no state (expected)
- [ ] Different search queries
- [ ] Filter combinations

---

## Sample Test Queries

### Good Test Queries

1. **Broad Query**: `"technology conference"`
   - Should return many results
   - Tests volume handling

2. **Specific Query**: `"AI summit in San Francisco"`
   - Should return fewer, targeted results
   - Tests filtering

3. **Date-Filtered Query**: 
   - Phrase: `"cybersecurity"`
   - Date From: Current month
   - Date To: Next month
   - Tests date filtering

4. **Event Type Query**:
   - Phrase: `"workshop"`
   - Event Type: `"workshop"`
   - Tests type matching

5. **Location Query**:
   - Phrase: `"conference"`
   - Location: `"online"`
   - Tests virtual event detection

---

## Success Criteria

### All Tests Pass If:

✅ Frontend loads without errors  
✅ Backend responds to health check  
✅ Search completes within 60 seconds  
✅ Results display correctly  
✅ Sorting works on all modes  
✅ Excel export downloads successfully  
✅ No CORS errors in console  
✅ No 404 or 500 errors  
✅ UI is responsive and smooth  
✅ Error handling works gracefully  

---

## Next Steps After Testing

### If Tests Pass ✅

1. Document any issues found
2. Test with real-world queries
3. Gather user feedback
4. Move to Increment 11 (Production Readiness)

### If Tests Fail ❌

1. Check browser console for errors
2. Check backend logs
3. Verify CORS configuration
4. Check network connectivity
5. Verify Ollama is running
6. Review error messages

---

## Testing Commands Quick Reference

```bash
# Backend health check
curl http://127.0.0.1:8000/api/v1/health

# Backend API docs
# Open: http://127.0.0.1:8000/docs

# Frontend UI
# Open: http://localhost:5173

# Check backend logs
# (In backend terminal)

# Check frontend dev server
# (In frontend terminal)

# Test search API
curl -X POST http://127.0.0.1:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"phrase": "test query"}'
```

---

**Ready to Test!** 🚀

Start with the simple search test in the UI, then work through the checklist.
