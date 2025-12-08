# Quick Testing Guide - UI Improvements

## How to Test the Changes

### Prerequisites
1. Backend running on http://localhost:8000
2. Frontend running on http://localhost:3000
3. Ollama running with qwen2.5:3b model

---

## Test 1: Date Display Fix

### Steps:
1. Open the web application
2. Enter search criteria and click "Start Search"
3. Wait for events to be extracted
4. Look at event cards in the results

### Expected Results:
✅ **BEFORE FIX**: Event cards showed "Date TBD"
✅ **AFTER FIX**: Event cards show actual dates like:
   - "January 15, 2024"
   - "March 3, 2023"
   - "December 25, 2022"

### Screenshot Areas:
- Event card date section (calendar icon + date text)

---

## Test 2: Event Details Modal

### Steps:
1. After search results appear, find any event card
2. Look for the blue "DETAILS" button (has info icon)
3. Click the "DETAILS" button
4. Modal dialog should open

### Expected Results:
✅ Modal displays a table with all event fields:

**Basic Info Section:**
- Event Type (color-coded chip: red for attacks, yellow for riots, blue for protests)
- Title
- Summary
- Perpetrator

**Location Section:**
- Complete location (venue, city, state, country)

**Time Section:**
- Event Date (formatted with time)
- Event Time (if available)

**People & Organizations:**
- Participants (as chips)
- Organizations (as chips)

**Impact Section:**
- Casualties (red chip for killed, yellow for injured)
- Impact description

**Source Section:**
- Source Name
- Source URL (clickable link)
- Article Published Date

**Quality Metrics:**
- Confidence Score (green ≥80%, yellow ≥60%, red <60%)
- Relevance Score (green ≥80%, yellow ≥60%, red <60%)

**Content:**
- Full Content (scrollable gray box)

### Actions to Test:
- [x] Click "Details" button → Modal opens
- [x] Scroll through all fields
- [x] Click Source URL → Opens in new tab
- [x] Click X button or outside modal → Modal closes
- [x] Test with multiple different events

---

## Test 3: Selective Export

### Test Case A: Export All Events
**Steps:**
1. After search results appear, DO NOT select any checkboxes
2. Click "Export All" button at the top
3. Excel file downloads

**Expected:**
✅ Excel file contains ALL events from search results
✅ File named: `events_export_YYYY-MM-DD.xlsx`

---

### Test Case B: Export Selected Events Only
**Steps:**
1. After search results appear, check 2-3 event checkboxes
2. Button text changes to "Export Selected (3)"
3. Click "Export Selected (3)" button
4. Excel file downloads

**Expected:**
✅ Excel file contains ONLY the 3 selected events
✅ File named: `events_export_YYYY-MM-DD.xlsx`
✅ Open file and verify event titles match selected ones

---

### Test Case C: Verify Selection State
**Steps:**
1. Select 2 events (check boxes)
2. Scroll down and select 1 more event
3. Note: Button shows "Export Selected (3)"
4. Uncheck 1 event
5. Note: Button shows "Export Selected (2)"
6. Uncheck all events
7. Note: Button shows "Export All"

**Expected:**
✅ Button label updates correctly based on selection count
✅ Checkbox state persists while scrolling

---

## Sample Test Scenarios

### Scenario 1: Complete Event
Search for: "capitol riot 2021"

**Expected Event Details:**
- Event Type: Riot / Civil Unrest
- Date: January 6, 2021
- Location: Washington, D.C., USA
- Perpetrator: Various groups
- Participants: Protesters, rioters
- Casualties: Multiple killed and injured
- Impact: Breach of US Capitol building

**Test:**
1. Verify date shows "January 6, 2021" (not "Date TBD")
2. Click Details → All fields populated
3. Select event → Export → Verify in Excel

---

### Scenario 2: Partial Data Event
Search for: "local protest"

**Expected:**
- Some fields may be N/A or empty
- Date should still display if available
- Details modal gracefully handles missing data

**Test:**
1. Verify missing fields show "N/A"
2. Details modal doesn't crash on missing data
3. Export still works with partial data

---

## Troubleshooting

### Problem: Still seeing "Date TBD"
**Possible Causes:**
1. Backend not sending `event_date` field
2. Frontend not rebuilt (need to restart dev server)
3. Browser cache (hard refresh: Ctrl+Shift+R)

**Solution:**
```bash
# Stop frontend
# Clear browser cache
# Restart frontend
cd frontend
npm start
```

---

### Problem: Details button missing
**Possible Cause:** Frontend not rebuilt

**Solution:**
```bash
cd frontend
npm install  # Install any missing dependencies
npm start    # Restart dev server
```

---

### Problem: Export downloads 0 events
**Possible Causes:**
1. No events selected and search returned 0 results
2. Backend API error

**Solution:**
- Check browser console for errors (F12)
- Check backend logs
- Verify search returned results before exporting

---

## Success Criteria

### ✅ All Tests Passed If:
1. **Date Display**: Real dates appear on event cards (no "Date TBD")
2. **Details Modal**: 
   - Button visible on all event cards
   - Modal opens with all 18 fields
   - All sections formatted correctly
   - Close button works
3. **Selective Export**:
   - Export All works (no selection)
   - Export Selected works (with selection)
   - Excel files contain correct events
   - Button label updates with count

---

## Performance Notes

### Expected Behavior:
- Details modal opens instantly (< 100ms)
- Export completes within 1-2 seconds
- No lag when selecting/deselecting events

### If Slow:
- Check number of events (100+ may be slower)
- Check system resources (16GB RAM optimized)
- Verify Ollama not processing during export

---

## Visual Checklist

When testing, look for these UI elements:

**Event Card:**
```
┌─────────────────────────────────────┐
│ [Type Chip]                         │
│ Event Title                         │
│ Summary text...                     │
│                                     │
│ 📅 January 15, 2024  ← Should show real date
│ 📍 Location                         │
│ 🏢 Perpetrator (if available)       │
│                                     │
│ [Relevance: 85%] [DETAILS] button   │
│                  └── NEW!           │
│ [Full Text] [Source]                │
└─────────────────────────────────────┘
```

**Details Modal:**
```
┌──────── Event Details ────────── [X]┐
│ ┌────────────────────────────────┐ │
│ │ Field Name    │ Value          │ │
│ │ Event Type    │ [Chip]         │ │
│ │ Title         │ ...            │ │
│ │ Summary       │ ...            │ │
│ │ Perpetrator   │ ...            │ │
│ │ Location      │ ...            │ │
│ │ Event Date    │ Jan 15, 2024   │ │
│ │ ...           │ ...            │ │
│ │ Full Content  │ ┌──────────┐   │ │
│ │               │ │ Scrollable│  │ │
│ │               │ │   Box     │  │ │
│ │               │ └──────────┘   │ │
│ └────────────────────────────────┘ │
└────────────────────────────────────┘
```

**Export Buttons:**
```
┌──────────────────────────────┐
│ 🔍 Search Results (15)       │
│                              │
│ [Select All] [Clear]         │
│ [Export All]                 │  ← When no selection
│                              │
│    OR                        │
│                              │
│ [Export Selected (3)]        │  ← When 3 selected
└──────────────────────────────┘
```

---

## Next Steps After Testing

If all tests pass:
1. ✅ Mark issues as resolved
2. ✅ Document any edge cases found
3. ✅ Update user documentation
4. ✅ Consider additional fields for future

If tests fail:
1. ❌ Note which test failed
2. ❌ Check browser console for errors
3. ❌ Check backend logs
4. ❌ Report issue with details
