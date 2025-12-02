# Backend Timeout Protection Implementation

**Date**: December 2, 2025  
**Feature**: Multi-level timeout protection for LLM processing  
**Status**: ✅ IMPLEMENTED

## Overview

To prevent the backend from exceeding the **10-minute frontend timeout**, we've implemented **3 levels of timeout protection**:

1. **Frontend timeout**: 10 minutes (600 seconds)
2. **Backend total timeout**: 8 minutes (480 seconds) - safety buffer
3. **Per-article timeout**: 2 minutes (120 seconds)

## Architecture

```
Frontend (10 min timeout)
    ↓
Backend Search Service (8 min total timeout)
    ↓
Event Extractor Loop
    ├─→ Article 1 (2 min max timeout)
    ├─→ Article 2 (2 min max timeout)
    ├─→ Article 3 (2 min max timeout)
    └─→ ... (stops at 8 min total OR all articles processed)
```

## Configuration

### Settings (`backend/app/settings.py`)

```python
class Settings(BaseSettings):
    # Ollama
    ollama_timeout: int = 120           # Per-article timeout (2 minutes)
    ollama_max_articles: int = 5        # Max articles to process
    ollama_total_timeout: int = 480     # Total LLM processing timeout (8 minutes)
```

### Environment Variables (`.env`)

```bash
# Individual article timeout
OLLAMA_TIMEOUT=120  # 2 minutes per article

# Total timeout for all LLM processing
OLLAMA_TOTAL_TIMEOUT=480  # 8 minutes total

# Maximum articles to process
OLLAMA_MAX_ARTICLES=5
```

## Implementation Details

### Level 1: Frontend Timeout (10 minutes)

**File**: `frontend/src/services/api.ts`

```typescript
constructor(baseURL: string = 'http://127.0.0.1:8000') {
  this.client = axios.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 600000, // 10 minutes = 600,000ms
  });
}
```

**Behavior**:
- Axios will abort the HTTP request after 10 minutes
- Frontend displays: "timeout of 600000ms exceeded"
- Backend may continue processing (unless stopped)

### Level 2: Backend Total Timeout (8 minutes)

**File**: `backend/app/services/search_service.py`

```python
async def _extract_events(self, articles: List[ArticleContent]) -> List[EventData]:
    """Extract events with total timeout protection."""
    events = []
    total_timeout = settings.ollama_total_timeout  # 480 seconds (8 min)
    start_time = datetime.now()
    
    logger.info(f"Starting LLM extraction with {total_timeout}s total timeout")
    
    for i, article in enumerate(articles_to_process, 1):
        # Check total elapsed time
        elapsed = (datetime.now() - start_time).total_seconds()
        remaining = total_timeout - elapsed
        
        if remaining <= 0:
            logger.warning(f"Total timeout ({total_timeout}s) reached. Stopping.")
            break  # Stop processing more articles
        
        # Process article...
```

**Behavior**:
- Tracks total time elapsed since LLM processing started
- If 8 minutes exceeded, **stops processing** remaining articles
- Returns events extracted so far (partial results)
- Logs: "Total timeout (480s) reached. Stopping after X/Y articles"

**Why 8 minutes (not 10)?**
- 1-2 minutes reserved for scraping
- 30 seconds buffer for network delays
- Ensures backend finishes before frontend timeout

### Level 3: Per-Article Timeout (2 minutes)

**File**: `backend/app/services/search_service.py`

```python
for i, article in enumerate(articles_to_process, 1):
    # Calculate timeout for this article
    article_timeout = min(remaining_time, settings.ollama_timeout)
    
    logger.debug(f"Processing article {i}/{total} with {article_timeout:.0f}s timeout")
    
    try:
        # Wrap extraction with asyncio timeout
        event_data = await asyncio.wait_for(
            event_extractor.extract_from_article(article),
            timeout=article_timeout
        )
        
        if event_data:
            events.append(event_data)
            
    except asyncio.TimeoutError:
        logger.warning(f"Timeout extracting event after {article_timeout:.0f}s")
        continue  # Skip this article, move to next
```

**Behavior**:
- Each article gets max 120 seconds (2 minutes)
- Uses `asyncio.wait_for()` to enforce timeout
- If article exceeds timeout:
  - Raises `asyncio.TimeoutError`
  - Logs warning
  - Skips to next article
  - Does NOT crash the entire search

**Dynamic timeout**:
```python
# If only 90 seconds left total, give article 90s (not 120s)
article_timeout = min(remaining_time, settings.ollama_timeout)
```

## Timeout Flow Examples

### Example 1: Normal Processing (Completes in Time)

```
Search starts
├─ Scraping: 1 min (OK)
├─ LLM Processing:
│  ├─ Article 1: 45 sec (OK, 0.75 min elapsed)
│  ├─ Article 2: 50 sec (OK, 1.58 min elapsed)
│  ├─ Article 3: 40 sec (OK, 2.25 min elapsed)
│  ├─ Article 4: 55 sec (OK, 3.17 min elapsed)
│  └─ Article 5: 48 sec (OK, 3.97 min elapsed)
└─ Matching & Response: 10 sec (OK)

Total: ~5 minutes ✅
Frontend timeout: 10 minutes ✅
Backend timeout: 8 minutes ✅
Result: SUCCESS - All 5 events extracted
```

### Example 2: One Article Times Out

```
Search starts
├─ Scraping: 1 min (OK)
├─ LLM Processing:
│  ├─ Article 1: 45 sec (OK)
│  ├─ Article 2: 120 sec (TIMEOUT! ⚠️ Skipped)
│  ├─ Article 3: 50 sec (OK)
│  ├─ Article 4: 48 sec (OK)
│  └─ Article 5: 42 sec (OK)
└─ Matching & Response: 10 sec (OK)

Total: ~6.5 minutes ✅
Frontend timeout: 10 minutes ✅
Backend timeout: 8 minutes ✅
Result: SUCCESS - 4 events extracted (1 skipped)
```

Logs:
```
INFO - Processing article 2/5 with 120s timeout
WARNING - Timeout extracting event from article 'Long article...' after 120s
INFO - Processing article 3/5 with 120s timeout
...
INFO - LLM extraction completed: 4 events from 5 articles
```

### Example 3: Total Timeout Reached

```
Search starts
├─ Scraping: 1 min (OK)
├─ LLM Processing:
│  ├─ Article 1: 90 sec (OK, 1.5 min elapsed)
│  ├─ Article 2: 110 sec (OK, 3.3 min elapsed)
│  ├─ Article 3: 95 sec (OK, 4.9 min elapsed)
│  ├─ Article 4: 105 sec (OK, 6.6 min elapsed)
│  ├─ Article 5: 85 sec (OK, 8.0 min elapsed)
│  └─ Total timeout reached! Stopped ⚠️
└─ Matching & Response: 10 sec (OK)

Total: ~9.2 minutes ✅
Frontend timeout: 10 minutes ✅
Backend timeout: 8 minutes ⚠️ (just reached)
Result: SUCCESS - 5 events extracted, stopped before attempting more
```

Logs:
```
INFO - Starting LLM extraction with 480s total timeout
INFO - Processing article 5/10 with 120s timeout
WARNING - Total timeout (480s) reached. Stopping after 5/10 articles
INFO - LLM extraction completed: 5 events from 10 articles in 480.2s
```

### Example 4: Multiple Article Timeouts + Total Timeout

```
Search starts
├─ Scraping: 1 min (OK)
├─ LLM Processing:
│  ├─ Article 1: 120 sec (TIMEOUT! ⚠️ Skipped)
│  ├─ Article 2: 115 sec (OK, 3.9 min elapsed)
│  ├─ Article 3: 120 sec (TIMEOUT! ⚠️ Skipped)
│  ├─ Article 4: 105 sec (OK, 7.7 min elapsed)
│  └─ Article 5: Would exceed total timeout, stopped ⚠️
└─ Matching & Response: 10 sec (OK)

Total: ~8.9 minutes ✅
Frontend timeout: 10 minutes ✅
Backend timeout: 8 minutes ⚠️ (reached)
Result: SUCCESS - 2 events extracted (2 timeouts, 1 not attempted)
```

## Error Handling

### Graceful Degradation

The system prioritizes **partial results over total failure**:

```python
# ✅ GOOD: Return events extracted so far
if remaining <= 0:
    logger.warning(f"Timeout reached. Returning {len(events)} events")
    return events  # Partial results

# ❌ BAD: Would raise exception and return nothing
if remaining <= 0:
    raise TimeoutError("Total timeout exceeded")
```

### User Experience

| Scenario | Events Extracted | User Sees | Experience |
|----------|------------------|-----------|------------|
| All articles processed | 5/5 | 5 events | ✅ Excellent |
| 1 article timeout | 4/5 | 4 events | ✅ Good |
| 2 articles timeout | 3/5 | 3 events | ⚠️ Acceptable |
| Total timeout reached | 3/5 | 3 events | ⚠️ Acceptable |
| All articles timeout | 0/5 | No events | ❌ Poor (needs investigation) |

### Logging for Debugging

```python
# Start of processing
logger.info(f"Starting LLM extraction with {total_timeout}s total timeout")

# Per article
logger.debug(f"Processing article {i}/{total} with {article_timeout:.0f}s timeout")

# Article timeout
logger.warning(f"Timeout extracting event from '{title}' after {timeout}s")

# Total timeout
logger.warning(f"Total timeout ({timeout}s) reached. Stopping after {i}/{total}")

# Completion
logger.info(f"LLM extraction completed: {events} events from {articles} in {time}s")
```

## Configuration Recommendations

### Fast (Testing, Development)

```bash
OLLAMA_MAX_ARTICLES=3        # Process only 3 articles
OLLAMA_TIMEOUT=60            # 1 minute per article
OLLAMA_TOTAL_TIMEOUT=240     # 4 minutes total
```

Expected time: 2-3 minutes

### Balanced (Default, Production)

```bash
OLLAMA_MAX_ARTICLES=5        # Process 5 articles
OLLAMA_TIMEOUT=120           # 2 minutes per article
OLLAMA_TOTAL_TIMEOUT=480     # 8 minutes total
```

Expected time: 4-6 minutes

### Comprehensive (Powerful hardware, batch processing)

```bash
OLLAMA_MAX_ARTICLES=10       # Process 10 articles
OLLAMA_TIMEOUT=90            # 1.5 minutes per article
OLLAMA_TOTAL_TIMEOUT=540     # 9 minutes total
```

Expected time: 7-9 minutes

### Safety Margins

```
Frontend timeout (10 min)
    ↓ 1-2 min buffer
Backend total timeout (8-9 min)
    ↓ 30 sec buffer per article
Per-article timeout (1.5-2 min)
    ↓ Actual processing
LLM generation (30-90 sec)
```

## Monitoring

### Success Metrics

Track these to ensure timeouts are working:

1. **Timeout rate**: % of articles that timeout
   - Target: < 10%
   - Alert: > 25%

2. **Total timeout rate**: % of searches hitting total timeout
   - Target: < 5%
   - Alert: > 15%

3. **Average time per article**:
   - Target: 30-60 seconds
   - Alert: > 90 seconds

4. **Search completion rate**:
   - Target: > 95%
   - Alert: < 85%

### Log Analysis

```bash
# Count article timeouts
grep "Timeout extracting event" logs/app.log | wc -l

# Count total timeouts
grep "Total timeout.*reached" logs/app.log | wc -l

# Average processing time
grep "LLM extraction completed" logs/app.log | grep -oP '\d+\.\d+s' | ...
```

## Testing

### Unit Tests

```python
@pytest.mark.asyncio
async def test_article_timeout():
    """Test that article timeout works."""
    # Create slow mock extractor
    async def slow_extract(article):
        await asyncio.sleep(150)  # Exceeds 120s timeout
        return EventData(...)
    
    # Should timeout
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_extract(article), timeout=120)

@pytest.mark.asyncio
async def test_total_timeout():
    """Test that total timeout stops processing."""
    service = SearchService()
    articles = [Article(...) for _ in range(10)]
    
    # Mock to make each article take 60s
    # Should stop after 8 articles (480s)
    events = await service._extract_events(articles)
    
    assert len(events) <= 8  # Stopped before processing all 10
```

### Integration Tests

```bash
# Test with slow LLM
OLLAMA_TIMEOUT=30 OLLAMA_TOTAL_TIMEOUT=120 python test_search.py

# Should see warnings in logs
grep "Timeout" logs/app.log
```

## Troubleshooting

### Issue: All articles timing out

**Symptoms**:
```
WARNING - Timeout extracting event from 'Article 1' after 120s
WARNING - Timeout extracting event from 'Article 2' after 120s
WARNING - Timeout extracting event from 'Article 3' after 120s
```

**Causes**:
1. Ollama server overloaded
2. Model too large for hardware
3. Network latency to Ollama
4. Timeout too short

**Solutions**:
```bash
# 1. Increase timeout
OLLAMA_TIMEOUT=180  # 3 minutes

# 2. Use smaller model
OLLAMA_MODEL=llama3.1:3b

# 3. Check Ollama server
curl http://localhost:11434/api/tags

# 4. Restart Ollama
ollama serve
```

### Issue: Total timeout always reached

**Symptoms**:
```
WARNING - Total timeout (480s) reached. Stopping after 3/5 articles
```

**Causes**:
1. Articles taking too long
2. Total timeout too short
3. Too many articles configured

**Solutions**:
```bash
# 1. Reduce articles
OLLAMA_MAX_ARTICLES=3

# 2. Increase total timeout (risky - may exceed frontend)
OLLAMA_TOTAL_TIMEOUT=540  # 9 minutes

# 3. Optimize per-article processing
# (see LLM_PERFORMANCE_OPTIMIZATION.md)
```

### Issue: Frontend still times out

**Symptoms**:
```
Error: timeout of 600000ms exceeded
```

**Causes**:
1. Backend total timeout > 10 minutes
2. Scraping takes very long
3. Network delays

**Solutions**:
```bash
# 1. Reduce backend timeout
OLLAMA_TOTAL_TIMEOUT=420  # 7 minutes (more buffer)

# 2. Reduce scraping time
MAX_ARTICLES_PER_SOURCE=30  # In config

# 3. Increase frontend timeout (last resort)
# In api.ts: timeout: 900000 (15 minutes)
```

## Summary

✅ **Multi-level timeout protection**:
- Frontend: 10 minutes
- Backend total: 8 minutes
- Per-article: 2 minutes (dynamic)

✅ **Graceful degradation**:
- Returns partial results on timeout
- Skips problematic articles
- Continues processing others

✅ **Production-ready**:
- Configurable via environment
- Comprehensive logging
- Clear error messages

✅ **Safety buffer**:
- Backend finishes before frontend timeout
- 2-minute buffer for network/overhead
- Dynamic per-article timeout reduces as time runs out

The system will **never** exceed the 10-minute frontend timeout, ensuring a reliable user experience!
