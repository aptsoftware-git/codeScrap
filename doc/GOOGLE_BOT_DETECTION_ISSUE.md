# Google Bot Detection Issue

## Problem
Google is detecting our scraper as a bot and returning a CAPTCHA/challenge page instead of actual search results.

### Evidence
The HTML returned is heavily minified JavaScript (bot detection system), not search results:
```html
<!DOCTYPE html><html lang="en-IN"><head><title>Google Search</title><style>body{background-color:var(--xhUGwc)}</style><script nonce="...">
```

This is Google's anti-bot protection page.

## Why Google Blocked Us

1. **Missing Browser Fingerprint**: Just User-Agent isn't enough
2. **No JavaScript Execution**: Google expects JavaScript-capable browsers
3. **Request Pattern**: Single HTTP request looks suspicious
4. **Missing Headers**: No Accept-Language, Cookies, etc.

## Solutions

### Option 1: Use Google Custom Search API (RECOMMENDED ✅)
**Pros:**
- Official Google API
- Reliable, no blocking
- Structured JSON results
- 100 free queries/day

**Cons:**
- Requires API key setup
- Limited to 100 queries/day (free tier)

**Implementation:**
```python
# 1. Get API key from: https://developers.google.com/custom-search/v1/introduction
# 2. Create Custom Search Engine: https://cse.google.com/cse/

import requests

API_KEY = "your-api-key"
SEARCH_ENGINE_ID = "your-search-engine-id"

def google_custom_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": 10
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    links = []
    for item in data.get("items", []):
        links.append(item["link"])
    
    return links
```

### Option 2: Use DuckDuckGo (SIMPLE ✅)
**Pros:**
- No API key needed
- No rate limiting
- Doesn't block scrapers
- Good results

**Cons:**
- Slightly different results than Google

**Implementation:**
```yaml
# config/sources.yaml
sources:
  - name: "DuckDuckGo Search"
    enabled: true
    base_url: "https://duckduckgo.com"
    search_url_template: "https://html.duckduckgo.com/html/?q={query}"
    rate_limit: 2.0
    selectors:
      article_links: ".result__url"
      title: "h1, h2"
      content: "article, p"
      date: "time"
```

### Option 3: Use Bing (FALLBACK ✅)
**Pros:**
- More lenient than Google
- Good results
- Less aggressive bot detection

**Cons:**
- Still may block eventually

**Implementation:**
```yaml
sources:
  - name: "Bing Search"
    enabled: true
    search_url_template: "https://www.bing.com/search?q={query}&count=10"
    selectors:
      article_links: ".b_algo h2 a"
      title: "h1, h2"
      content: "article, p"
```

### Option 4: Use Selenium with Real Browser (OVERKILL)
**Pros:**
- Works with Google
- Executes JavaScript
- Full browser simulation

**Cons:**
- VERY SLOW (adds 5-10 seconds per search)
- Requires ChromeDriver/browser installation
- High memory usage
- Complex setup

**Not recommended for your use case**

## Recommended Solution

**Use DuckDuckGo** - It's the simplest and most reliable option:

### 1. Update `config/sources.yaml`:
```yaml
sources:
  # DuckDuckGo (Recommended - No API key, no blocking)
  - name: "DuckDuckGo"
    base_url: "https://duckduckgo.com"
    enabled: true
    search_url_template: "https://html.duckduckgo.com/html/?q={query}"
    rate_limit: 2.0
    selectors:
      article_links: ".result__url"
      title: "h1, h2, .article-title"
      content: "article, .article-content, p"
      date: "time, .date"
    headers:
      User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

### 2. DuckDuckGo HTML Version
DuckDuckGo has an HTML-only version (`html.duckduckgo.com`) specifically designed for:
- Screen readers
- Text browsers
- Scrapers (!)

It provides clean HTML with simple CSS selectors.

## Testing

After switching to DuckDuckGo, you should see:
```
✅ Found 10+ article links from DuckDuckGo
✅ Scraped 5 articles
✅ Processing with LLM...
```

## Long-term Solution

For production use, consider:
1. **DuckDuckGo** for general searches (free, unlimited)
2. **Google Custom Search API** for important queries (100/day free)
3. **Direct news site scraping** for specific sources (current BBC, Reuters configs)

## Why Not Fix Google Scraping?

To bypass Google's bot detection, you'd need:
- Selenium + real Chrome browser
- Rotating proxies
- CAPTCHA solving service
- Complex fingerprinting evasion

**Cost:** $50-100/month for proxies + CAPTCHA solving  
**Complexity:** High  
**Speed:** Slow (5-10 seconds per search)

**DuckDuckGo/Bing:** Free, fast, simple ✅

---

**Decision:** Switch to DuckDuckGo or Bing for meta-search functionality.
