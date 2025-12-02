# Increment 10 Testing Guide

## Quick Start

Both servers are now running:
- ✅ **Backend**: http://127.0.0.1:8000
- ✅ **Frontend**: http://localhost:5173

## Testing Steps

### 1. Open Frontend
Open your browser to: **http://localhost:5173**

### 2. Test Search
1. Enter search phrase: `"AI conference"`
2. (Optional) Add location: `"San Francisco"`
3. Click **Search** button
4. Wait 30-60 seconds for results

### 3. Test Results Display

#### View Results
- ✅ Events appear as cards with metadata
- ✅ Relevance scores shown with colors
- ✅ Statistics shown at top (matched/extracted/scraped)

#### Test Sorting
- Click **Sort By** dropdown
- Try: Relevance (default), Date, Title
- Verify events re-order correctly

#### Test Selection
- ✅ Click checkbox on individual cards
- ✅ Cards show blue border when selected
- ✅ Selection count appears in alert
- ✅ Click **Select All** button
- ✅ All events selected
- ✅ Click **Clear** button
- ✅ All selections removed

### 4. Test Export

#### Export All Events
1. Make sure no events are selected
2. Button should say **"Export All to Excel"**
3. Click the button
4. Wait for download
5. Green success message appears
6. Excel file downloads automatically

#### Export Selected Events
1. Select 2-3 events by clicking checkboxes
2. Button should say **"Export X Selected to Excel"**
3. Click the button
4. Wait for download
5. Green success message appears
6. Excel file downloads with only selected events

#### Verify Excel File
1. Open the downloaded Excel file
2. Check columns:
   - Title
   - Date
   - Location (City, State, Country, Venue)
   - Event Type
   - Description
   - URL
   - Organizer
   - Relevance Score
   - Source URL
3. Verify data is formatted correctly
4. Check that date is formatted
5. Verify relevance score is a percentage

### 5. Test Error Handling

#### Backend Connection Error
1. Stop backend server (Ctrl+C in backend terminal)
2. Try to search in frontend
3. Should show error: "Cannot connect to server..."

#### Validation Errors
1. Leave search phrase empty
2. Click Search
3. Should show error: "Please enter a search phrase"

4. Enter dates with start > end
5. Click Search
6. Should show error: "Start date must be before end date"

#### Export Error
1. Disconnect internet or stop backend
2. Try to export
3. Should show red error snackbar

### 6. Test User Experience

#### Loading States
- ✅ Search button shows "Searching..." with spinner
- ✅ Form fields disabled during search
- ✅ Export button shows "Exporting..." during export

#### Interactive Elements
- ✅ Click on event title → Opens source in new tab
- ✅ Click on "Source" link → Opens original article
- ✅ Hover over cards → Shadow effect
- ✅ Click anywhere on card → Toggles selection

#### Feedback
- ✅ Success snackbar after export (green)
- ✅ Error snackbar on failure (red)
- ✅ Selection alert shows count
- ✅ Processing time shown in results

## Expected Results

### Sample Search: "protest in Mumbai"

**Should Return:**
- 5-10 matching events
- Processing time: 30-60 seconds
- Events sorted by relevance
- Each event showing:
  - Title from article
  - Date (if found)
  - Location: Mumbai, India
  - Event type: protest/demonstration
  - Description/summary
  - Relevance score: 60-90%

### Sample Export

**Excel file should contain:**
- Filename: `events_protest_in_Mumbai_2025-12-02.xlsx`
- Header row with colored background
- Auto-sized columns
- Formatted dates
- All metadata preserved

## Troubleshooting

### Frontend won't start
```bash
cd frontend
npm install
npm run dev
```

### Backend won't start
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### TypeScript errors
```bash
cd frontend
npm run build
# Check for compilation errors
```

### CORS errors
- Check backend `app/main.py`
- CORS origins should include `http://localhost:5173`

## Performance Benchmarks

### Search Performance
- **Fast**: 20-30 seconds (3-5 sources)
- **Normal**: 30-60 seconds (5-10 sources)
- **Slow**: 60-120 seconds (10+ sources or slow sites)

### Export Performance
- **Small** (1-10 events): < 1 second
- **Medium** (10-50 events): 1-2 seconds
- **Large** (50+ events): 2-5 seconds

## Known Issues

1. **Selection persists across sorts** ✅ (Working as designed)
2. **No pagination** - All results shown (OK for <100 events)
3. **No event detail modal** - Use source link instead
4. **Selection lost on new search** ✅ (Working as designed)

## Success Criteria

All tests should pass:
- [ ] Search returns results
- [ ] Results display with all metadata
- [ ] Sorting works (relevance/date/title)
- [ ] Selection works (individual/all/clear)
- [ ] Export all works
- [ ] Export selected works
- [ ] Excel file formatted correctly
- [ ] Error messages shown correctly
- [ ] Loading states work
- [ ] Success feedback works

## Next Steps

If all tests pass:
✅ **Increment 10 COMPLETE**
➡️ **Ready for Increment 11: Production Readiness**

---

**End of Testing Guide**
