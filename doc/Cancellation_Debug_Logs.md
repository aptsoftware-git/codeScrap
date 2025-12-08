# Cancellation Debug Logs - What to Look For

## Added Comprehensive Logging

I've added detailed logging with **[TAGS]** to help debug the cancellation issue. All logs are prefixed with tags so you can easily filter and understand the flow.

---

## Log Tags

### **[CANCEL-REQUEST]** - Cancel API Endpoint
Logs when the cancel button is clicked and the API endpoint receives the request.

**Example**:
```
INFO | [CANCEL-REQUEST] Received cancel request for session abc123
INFO | [CANCEL-REQUEST] Current session status: IN_PROGRESS
INFO | [CANCEL-REQUEST] Session abc123 marked as cancelled in session store
INFO | [CANCEL-REQUEST] Session abc123 is_cancelled: True
INFO | [CANCEL-REQUEST] Session abc123 cancelled. 2 events extracted before cancellation.
```

---

### **[SESSION-STORE]** - Session Store Operations
Logs when the session is added to the cancelled set.

**Example**:
```
INFO | [SESSION-STORE] Cancelling session abc123
INFO | [SESSION-STORE] Cancelled sessions before: set()
INFO | [SESSION-STORE] Cancelled sessions after: {'abc123'}
WARNING | [SESSION-STORE] Session abc123 marked as cancelled
```

---

### **[CANCEL-CHECK]** - Cancellation Checks
Logs every time the code checks if the session is cancelled. Shows the result of the check.

**Example**:
```
INFO | [CANCEL-CHECK] Before scraping - Session abc123 cancelled: False
INFO | [CANCEL-CHECK] After scraping - Session abc123 cancelled: True
INFO | [CANCEL-CHECK] Before source 1/3 (CNN) - Session abc123 cancelled: True
INFO | [CANCEL-CHECK] Before article 5/20 - Session abc123 cancelled: True
INFO | [CANCEL-CHECK] Before LLM extraction article 3 - Session abc123 cancelled: False
INFO | [CANCEL-CHECK] After LLM extraction article 3 - Session abc123 cancelled: True
```

---

### **[CANCELLED]** - Cancellation Detected
Logs when cancellation is detected and the operation stops.

**Example**:
```
WARNING | [CANCELLED] Search cancelled for session abc123 before scraping
WARNING | [CANCELLED] Search cancelled for session abc123 during scraping at source CNN
WARNING | [CANCELLED] Search cancelled for session abc123 after scraping CNN
WARNING | [CANCELLED] Scraping cancelled before fetching search results from Google
WARNING | [CANCELLED] Scraping cancelled at article 8/20 from CNN
WARNING | [CANCELLED] Search cancelled for session abc123 before extracting article 5
WARNING | [CANCELLED] Search cancelled for session abc123 after extracting article 4
```

---

### **[SCRAPING]** - Web Scraping Operations
Logs all scraping activities.

**Example**:
```
INFO | [SCRAPING] Starting scraping for session abc123
INFO | [SCRAPING] Starting scraping from 3 sources for query: 'attack' - Session: abc123
INFO | [SCRAPING] Starting source 1/3: CNN - Session abc123
INFO | [SCRAPING] Fetching search results from CNN: https://...
INFO | [SCRAPING] Fetching article 1/20 from CNN: https://...
INFO | [SCRAPING] Successfully scraped article 1 from CNN
INFO | [SCRAPING] Failed to scrape article 2 from CNN
INFO | [SCRAPING] Got 15 articles from CNN - Session abc123
INFO | [SCRAPING] Total articles scraped: 35 - Session abc123
INFO | [SCRAPING] Completed scraping for session abc123 - Got 35 articles
```

---

### **[LLM]** - LLM Processing Operations
Logs all LLM extraction activities.

**Example**:
```
INFO | [LLM] Starting extraction for article 1/20 - Session abc123
INFO | [LLM] Completed extraction for article 1/20 - Session abc123
```

---

## Test Scenario: Click Cancel Immediately After Search

### **What Should Happen** ✅

1. **User clicks Search**:
   ```
   INFO | Created session abc123 with status PENDING
   INFO | [SCRAPING] Starting scraping for session abc123
   INFO | [SCRAPING] Starting scraping from 3 sources...
   INFO | [SCRAPING] Starting source 1/3: CNN
   INFO | [SCRAPING] Fetching search results from CNN: https://...
   ```

2. **User clicks Cancel immediately**:
   ```
   INFO | [CANCEL-REQUEST] Received cancel request for session abc123
   INFO | [CANCEL-REQUEST] Current session status: IN_PROGRESS
   INFO | [SESSION-STORE] Cancelling session abc123
   INFO | [SESSION-STORE] Cancelled sessions after: {'abc123'}
   WARNING | [SESSION-STORE] Session abc123 marked as cancelled
   INFO | [CANCEL-REQUEST] Session abc123 is_cancelled: True ✅
   ```

3. **Next cancellation check should detect it**:
   ```
   INFO | [CANCEL-CHECK] Before source 2/3 - Session abc123 cancelled: True ✅
   WARNING | [CANCELLED] Search cancelled for session abc123 at source CNN ✅
   ```
   OR
   ```
   INFO | [CANCEL-CHECK] After source 1/3 (CNN) - Session abc123 cancelled: True ✅
   WARNING | [CANCELLED] Search cancelled for session abc123 after scraping CNN ✅
   ```

4. **No further processing**:
   ```
   ❌ Should NOT see: [SCRAPING] Starting source 2/3
   ❌ Should NOT see: [LLM] Starting extraction
   ❌ Should NOT see: [SCRAPING] Fetching article X from source 2
   ```

---

### **What You're Seeing** ❌

Please run a test and share the logs. Look for:

1. **When does `[CANCEL-REQUEST]` appear?**
   - Is it logged at all?
   - What's the timestamp?

2. **What is `is_cancelled` returning?**
   - Does `[CANCEL-REQUEST] Session abc123 is_cancelled: True` appear?
   - Or does it show `False`?

3. **When does `[CANCEL-CHECK]` next happen?**
   - What does it return? True or False?
   - How long after the cancel request?

4. **Does processing continue?**
   - Do you see `[SCRAPING]` logs after `[CANCELLED]`?
   - Do you see `[LLM]` logs after cancellation?

---

## Possible Issues to Check

### Issue 1: Cancel Request Not Reaching Backend
**Symptoms**:
- No `[CANCEL-REQUEST]` logs appear
- Processing continues without any cancellation checks showing True

**Diagnosis**: Frontend not sending cancel request properly

---

### Issue 2: Session ID Mismatch
**Symptoms**:
- `[CANCEL-REQUEST]` shows session ID "abc123"
- `[CANCEL-CHECK]` shows different session ID "xyz456"
- Cancellation never detected

**Diagnosis**: Frontend and backend using different session IDs

---

### Issue 3: Timing Issue (Race Condition)
**Symptoms**:
- `[CANCEL-REQUEST] is_cancelled: True` ✅
- `[CANCEL-CHECK]` immediately after shows `cancelled: False` ❌
- Processing continues

**Diagnosis**: Lambda function capturing old session_id or async timing issue

---

### Issue 4: Lambda Closure Issue
**Symptoms**:
- Cancellation works for main loop but NOT in scraper_manager
- `[CANCELLED]` appears in search_service but NOT in scraper_manager

**Diagnosis**: The lambda function `lambda: self.session_store.is_cancelled(session_id)` might be capturing the wrong value

---

## How to Test

1. **Start a search** (any query)
2. **Click Cancel immediately** (within 1-2 seconds)
3. **Copy ALL backend logs** from the terminal
4. **Share the logs** and look for:
   - All `[CANCEL-REQUEST]` entries
   - All `[SESSION-STORE]` entries  
   - All `[CANCEL-CHECK]` entries
   - All `[CANCELLED]` entries
   - All `[SCRAPING]` entries after cancel
   - All `[LLM]` entries after cancel

---

## Expected Log Flow (Successful Cancellation)

```
# Search starts
INFO | Created session 12345 with status PENDING
INFO | [SCRAPING] Starting scraping for session 12345

# User clicks cancel
INFO | [CANCEL-REQUEST] Received cancel request for session 12345
INFO | [SESSION-STORE] Cancelled sessions after: {'12345'}
INFO | [CANCEL-REQUEST] Session 12345 is_cancelled: True

# Next check detects it
INFO | [CANCEL-CHECK] Before source 2/3 - Session 12345 cancelled: True
WARNING | [CANCELLED] Search cancelled for session 12345 during scraping

# Processing stops - NO MORE LOGS after this
```

---

## Test Now

Please run the test and share:
1. The complete backend logs
2. What you see in the UI (button state)
3. Approximate timing (when you clicked search vs cancel)

This will help identify exactly where the cancellation is failing!
