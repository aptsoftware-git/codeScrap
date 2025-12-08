# Per-Source Configuration Guide

## Overview

The system now supports **per-source configuration** for scraping limits, allowing fine-grained control over how many URLs are extracted and how many articles are processed for each news source.

## Configuration Hierarchy

Settings follow this priority (highest to lowest):
1. **Function parameters** (if provided in code)
2. **Per-source configuration** (in `config/sources.yaml`)
3. **Global defaults** (in `.env` file)

## Configuration Variables

### Global Settings (in `.env`)

```bash
# Scraping Limits (Global Defaults)
MAX_SEARCH_RESULTS=10                # Maximum URL results to extract from search page
MAX_ARTICLES_TO_PROCESS=5            # Maximum articles to scrape and process with LLM
```

### Per-Source Settings (in `config/sources.yaml`)

```yaml
sources:
  - name: "DuckDuckGo"
    base_url: "https://duckduckgo.com"
    enabled: true
    search_url_template: "https://html.duckduckgo.com/html/?q={query}"
    rate_limit: 2.0
    
    # Scraping limits (optional - if not set, uses global defaults)
    max_search_results: 10      # Extract up to 10 URLs from search results
    max_articles_to_process: 5  # Scrape and process up to 5 articles with LLM
    
    selectors:
      # ... selectors config ...
```

## Validation Rules

The system automatically validates configuration values:

1. **`max_search_results > 0`**
   - If invalid (≤ 0), defaults to 10
   - Example: `max_search_results: -5` → auto-corrected to `10`

2. **`max_search_results >= max_articles_to_process`**
   - If `max_search_results < max_articles_to_process`, they are made equal
   - Example: `max_search_results: 3, max_articles_to_process: 5` → both become `5`
   - Reason: Can't process more articles than URLs extracted

## Default Values

- **`max_search_results`**: 10 URLs
- **`max_articles_to_process`**: 5 articles

## How It Works

### 1. URL Extraction Phase
```
Search Query → News Source → Extract URLs → Limit to max_search_results
```

### 2. Article Scraping Phase
```
URL List → Scrape Articles → Limit to max_articles_to_process
```

### 3. LLM Event Extraction Phase
```
Articles → Ollama LLM → Extract Events (1-3+ events per article)
```

## Examples

### Example 1: Use Global Defaults

**`.env`:**
```bash
MAX_SEARCH_RESULTS=10
MAX_ARTICLES_TO_PROCESS=5
```

**`sources.yaml`:**
```yaml
sources:
  - name: "DuckDuckGo"
    enabled: true
    # No max_search_results or max_articles_to_process specified
    # Will use global defaults: 10 URLs, 5 articles
```

**Result:** Extracts 10 URLs, scrapes 5 articles

---

### Example 2: Override Per Source

**`.env`:**
```bash
MAX_SEARCH_RESULTS=10
MAX_ARTICLES_TO_PROCESS=5
```

**`sources.yaml`:**
```yaml
sources:
  - name: "DuckDuckGo"
    enabled: true
    max_search_results: 20        # Override global
    max_articles_to_process: 10   # Override global
```

**Result:** Extracts 20 URLs, scrapes 10 articles (ignores global defaults)

---

### Example 3: Different Limits for Different Sources

**`sources.yaml`:**
```yaml
sources:
  - name: "DuckDuckGo"
    enabled: true
    max_search_results: 15
    max_articles_to_process: 8
    
  - name: "BBC News"
    enabled: true
    max_search_results: 5
    max_articles_to_process: 3
```

**Result:**
- DuckDuckGo: 15 URLs, 8 articles
- BBC News: 5 URLs, 3 articles

---

### Example 4: Validation in Action

**`sources.yaml`:**
```yaml
sources:
  - name: "DuckDuckGo"
    enabled: true
    max_search_results: 3         # Too low!
    max_articles_to_process: 5
```

**Auto-correction:** System logs warning and sets `max_search_results = 5` to match `max_articles_to_process`

**Final Result:** Extracts 5 URLs, scrapes 5 articles

---

## Performance Tuning

### For 16GB RAM Systems (Intel i7)

**`.env`:**
```bash
MAX_SEARCH_RESULTS=10
MAX_ARTICLES_TO_PROCESS=1        # Process only 1 article at a time
MAX_CONCURRENT_LLM=1             # Only 1 LLM instance at a time
```

### For 64GB RAM Systems (Dual Xeon Gold 6140)

**`.env`:**
```bash
MAX_SEARCH_RESULTS=20
MAX_ARTICLES_TO_PROCESS=5        # Process up to 5 articles
MAX_CONCURRENT_LLM=4             # 4 parallel LLM instances
```

## Migration from Legacy Configuration

### Old Way (REMOVED)
```bash
OLLAMA_MAX_ARTICLES=5  # Only controlled LLM processing, not URL extraction
```
**Status:** This parameter has been **completely removed**. It is no longer supported.

### New Way (REQUIRED)
```bash
MAX_SEARCH_RESULTS=10            # Control URL extraction
MAX_ARTICLES_TO_PROCESS=5        # Control article scraping AND LLM processing
```

**Migration Steps:**
1. Remove `OLLAMA_MAX_ARTICLES` from your `.env` file
2. Add `MAX_SEARCH_RESULTS` and `MAX_ARTICLES_TO_PROCESS`
3. Restart the backend server

## Code Changes Summary

### Modified Files

1. **`backend/app/settings.py`**
   - Added `max_search_results: int = 10`
   - Added `max_articles_to_process: int = 5`
   - Removed `ollama_max_articles` (old parameter)

2. **`backend/app/models.py`**
   - Added `max_search_results: Optional[int]` to `SourceConfig`
   - Added `max_articles_to_process: Optional[int]` to `SourceConfig`

3. **`backend/app/services/scraper_manager.py`**
   - Updated `scrape_search_results()` signature with new parameters
   - Added validation logic for limits
   - Added hierarchical config resolution (param > source > global)
   - Limits URL extraction to `max_search_results`

4. **`backend/app/services/search_service.py`**
   - Updated `search()` to use `max_articles_to_process`
   - Updated `search_stream()` to use `max_articles_to_process`
   - Updated `_scrape_articles()` to pass settings correctly
   - Updated `_extract_events()` to use new setting name

5. **`config/sources.yaml`**
   - Added documentation comments
   - Added example configuration for `max_search_results` and `max_articles_to_process`

6. **`backend/.env.intel_i7`**
   - Added new global settings
   - Marked legacy setting as DEPRECATED

## Logging

The system logs configuration decisions for debugging:

```
[INFO] Source DuckDuckGo: max_search_results=10, max_articles_to_process=5
[INFO] Found 25 article links from DuckDuckGo (limited to 10)
[WARN] Invalid max_search_results (-5), using default 10
[INFO] max_search_results (3) < max_articles_to_process (5), setting max_search_results = 5
```

## Testing

To verify the configuration is working:

1. **Check logs** for configuration messages
2. **Monitor article counts** in search results
3. **Verify per-source limits** by enabling multiple sources with different settings

## Troubleshooting

### Issue: System ignoring per-source limits

**Solution:** Ensure YAML syntax is correct (proper indentation, no tabs)

```yaml
# WRONG (wrong indentation)
sources:
- name: "DuckDuckGo"
  max_search_results: 10

# CORRECT
sources:
  - name: "DuckDuckGo"
    max_search_results: 10
```

### Issue: Getting fewer articles than configured

**Possible causes:**
1. Not enough URLs found in search results
2. Article scraping failures (network errors, invalid HTML)
3. Validation auto-correction

**Debug:** Check logs for `[SCRAPING]` messages showing actual counts

## Best Practices

1. **Start with conservative limits** (5-10 articles) and increase gradually
2. **Monitor memory usage** when increasing limits
3. **Set lower limits for slower sources** (reduces timeouts)
4. **Use per-source config** for sources with different content quality
5. **Test changes** before deploying to production

## Future Enhancements

Potential future improvements:
- Dynamic adjustment based on source response time
- Automatic memory-based limit calculation
- Per-query override via API
- Rate limiting based on source capacity
