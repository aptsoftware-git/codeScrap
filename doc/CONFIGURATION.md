# Configuration Guide

Complete guide for configuring the Event Scraper & Analyzer application.

---

## Table of Contents

1. [Overview](#overview)
2. [Backend Configuration](#backend-configuration)
3. [Frontend Configuration](#frontend-configuration)
4. [Ollama Configuration](#ollama-configuration)
5. [Sources Configuration](#sources-configuration)
6. [Performance Tuning](#performance-tuning)
7. [Security Configuration](#security-configuration)
8. [Logging Configuration](#logging-configuration)
9. [Common Scenarios](#common-scenarios)
10. [Validation & Testing](#validation--testing)

---

## Overview

### Configuration Files

The application uses environment variables for configuration:

**Backend:**
- `backend/.env` - Environment variables (create from `.env.example`)
- `config/sources.json` - News sources configuration

**Frontend:**
- `frontend/.env` - Frontend environment variables (create from `.env.example`)

### Configuration Priority

1. Environment variables (highest priority)
2. `.env` file
3. Default values in code (lowest priority)

### Quick Start

```bash
# Backend
cd backend
cp .env.example .env
# Edit .env with your settings
nano .env

# Frontend
cd frontend
cp .env.example .env
# Edit .env with your API URL
nano .env
```

---

## Backend Configuration

### Application Settings

```bash
# Application Mode
DEBUG=false                    # Enable debug mode (true/false)
LOG_LEVEL=INFO                 # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
ENVIRONMENT=production         # Environment (development, production, staging)
```

**Recommendations:**
- **Development:** `DEBUG=true`, `LOG_LEVEL=DEBUG`
- **Production:** `DEBUG=false`, `LOG_LEVEL=INFO`
- **Testing:** `DEBUG=false`, `LOG_LEVEL=WARNING`

### Server Configuration

```bash
# Server Settings
HOST=0.0.0.0                   # Bind address (0.0.0.0 = all interfaces)
PORT=8000                      # Port number
RELOAD=false                   # Auto-reload on code changes (dev only)
WORKERS=4                      # Number of worker processes
```

**Guidelines:**
- **Development:** `HOST=127.0.0.1`, `RELOAD=true`, `WORKERS=1`
- **Production:** `HOST=0.0.0.0`, `RELOAD=false`, `WORKERS=<CPU cores>`
- **Behind Proxy:** `HOST=127.0.0.1` (if using Nginx/Apache)

**Worker Calculation:**
```python
# Recommended workers
workers = (2 * CPU_cores) + 1

# Examples:
# 2 cores: 5 workers
# 4 cores: 9 workers
# 8 cores: 17 workers
```

### CORS Configuration

```bash
# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com
```

**Examples:**

**Development:**
```bash
CORS_ORIGINS=http://localhost:5173
```

**Production (multiple domains):**
```bash
CORS_ORIGINS=https://events.company.com,https://www.company.com
```

**Production (subdomain wildcard - requires code change):**
```python
# In main.py, replace allow_origins with:
allow_origin_regex=r"https://.*\.company\.com"
```

### Rate Limiting

```bash
# Rate Limits
RATE_LIMIT_SEARCH=10           # Max searches per minute
RATE_LIMIT_EXPORT=5            # Max exports per minute
RATE_LIMIT_WINDOW=60           # Time window in seconds
```

**Recommendations:**
- **Light usage:** `RATE_LIMIT_SEARCH=5`, `RATE_LIMIT_EXPORT=3`
- **Normal usage:** `RATE_LIMIT_SEARCH=10`, `RATE_LIMIT_EXPORT=5`
- **Heavy usage:** `RATE_LIMIT_SEARCH=20`, `RATE_LIMIT_EXPORT=10`
- **No limit:** Set to very high number like `1000`

### Session Management

```bash
# Session Settings
SESSION_CLEANUP_HOURS=24       # Remove sessions older than X hours
SESSION_CLEANUP_INTERVAL=3600  # Cleanup check interval (seconds)
```

**Guidelines:**
- **Short-term:** `SESSION_CLEANUP_HOURS=2` (saves disk space)
- **Standard:** `SESSION_CLEANUP_HOURS=24` (1 day)
- **Extended:** `SESSION_CLEANUP_HOURS=168` (1 week)

### Performance Settings

```bash
# Performance
MAX_CONCURRENT_SCRAPES=5       # Max parallel scraping operations
MAX_EVENTS_PER_ARTICLE=10      # Max events to extract per article
ENABLE_CACHING=true            # Enable result caching
CACHE_TTL=3600                 # Cache time-to-live (seconds)
```

**Tuning:**

**For High Performance:**
```bash
MAX_CONCURRENT_SCRAPES=10
MAX_EVENTS_PER_ARTICLE=5
ENABLE_CACHING=true
CACHE_TTL=1800
```

**For Accuracy:**
```bash
MAX_CONCURRENT_SCRAPES=3
MAX_EVENTS_PER_ARTICLE=20
ENABLE_CACHING=false
```

**For Balanced:**
```bash
MAX_CONCURRENT_SCRAPES=5
MAX_EVENTS_PER_ARTICLE=10
ENABLE_CACHING=true
CACHE_TTL=3600
```

---

## Frontend Configuration

### API Configuration

```bash
# API Endpoint
VITE_API_BASE_URL=http://localhost:8000

# Request Settings
VITE_API_TIMEOUT=300000        # Request timeout (ms) - 5 minutes
VITE_SEARCH_TIMEOUT=300000     # Search timeout (ms) - 5 minutes
```

**Environments:**

**Development:**
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=300000
```

**Production:**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_API_TIMEOUT=180000        # 3 minutes
```

**Production (same domain):**
```bash
VITE_API_BASE_URL=/api         # Nginx proxy to backend
VITE_API_TIMEOUT=180000
```

### Application Settings

```bash
# Application Info
VITE_APP_NAME=Event Scraper
VITE_APP_VERSION=1.0.0

# Features
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=false

# UI Settings
VITE_ITEMS_PER_PAGE=20
VITE_MAX_EXPORT_EVENTS=1000
```

**Customization:**
- Adjust `VITE_ITEMS_PER_PAGE` based on typical result size
- Set `VITE_MAX_EXPORT_EVENTS` based on Excel limitations

---

## Ollama Configuration

### Connection Settings

```bash
# Ollama Server
OLLAMA_URL=http://localhost:11434    # Ollama API URL
OLLAMA_TIMEOUT=120                   # Request timeout (seconds)
OLLAMA_RETRIES=3                     # Retry attempts on failure
```

**Scenarios:**

**Local Ollama:**
```bash
OLLAMA_URL=http://localhost:11434
OLLAMA_TIMEOUT=120
```

**Remote Ollama:**
```bash
OLLAMA_URL=http://ollama-server.company.com:11434
OLLAMA_TIMEOUT=180                   # Longer timeout for network
```

**Ollama with Authentication:**
```python
# Requires code modification in ollama_service.py
# Add headers to requests:
headers = {
    "Authorization": f"Bearer {OLLAMA_API_KEY}"
}
```

### Model Configuration

```bash
# Model Settings
OLLAMA_MODEL=llama3.1:8b             # Model name
OLLAMA_TEMPERATURE=0.1               # Randomness (0.0-1.0)
OLLAMA_NUM_CTX=4096                  # Context window size
OLLAMA_NUM_PREDICT=1024              # Max tokens to generate
```

**Model Selection:**

| Model | RAM Required | Speed | Accuracy | Best For |
|-------|--------------|-------|----------|----------|
| llama3.1:8b | 16 GB | Fast | Good | Most scenarios |
| llama2:13b | 24 GB | Medium | Better | Higher accuracy |
| llama2:70b | 64+ GB | Slow | Best | Maximum accuracy |
| mistral:7b | 16 GB | Fast | Good | Fast processing |

**Temperature Guidelines:**
- **0.0-0.2:** Factual extraction (recommended)
- **0.3-0.5:** Balanced creativity
- **0.6-1.0:** Creative writing (not recommended)

**Context Window:**
```bash
# For short articles
OLLAMA_NUM_CTX=2048

# For medium articles (default)
OLLAMA_NUM_CTX=4096

# For long articles
OLLAMA_NUM_CTX=8192
```

---

## Sources Configuration

### File Location

```
config/sources.json
```

### Structure

```json
{
  "sources": [
    {
      "name": "Example News",
      "url": "https://example.com/news",
      "enabled": true,
      "scrape_config": {
        "article_selector": "article.news-item",
        "title_selector": "h2.title",
        "content_selector": "div.content",
        "date_selector": "time.published",
        "link_selector": "a.read-more"
      }
    }
  ]
}
```

### Configuration Options

**Source Properties:**

```json
{
  "name": "Source Name",           // Display name
  "url": "https://...",            // Source URL
  "enabled": true,                 // Enable/disable source
  "priority": 1,                   // Priority (1=highest)
  "timeout": 30,                   // Override global timeout
  "scrape_config": { ... }         // CSS selectors
}
```

**Scrape Configuration:**

```json
{
  "article_selector": "...",       // Container for each article
  "title_selector": "...",         // Article title
  "content_selector": "...",       // Article body/description
  "date_selector": "...",          // Publication date
  "link_selector": "...",          // Link to full article
  "date_format": "%Y-%m-%d"        // Optional: date parsing format
}
```

### Adding Sources

1. **Inspect the website** using browser dev tools
2. **Identify CSS selectors** for key elements
3. **Test selectors** in browser console:
   ```javascript
   document.querySelectorAll('article.news-item')
   ```
4. **Add to sources.json**
5. **Test the configuration**:
   ```bash
   curl http://localhost:8000/sources
   ```

### Example Sources

**News Website:**
```json
{
  "name": "Tech News Daily",
  "url": "https://technews.com/latest",
  "enabled": true,
  "scrape_config": {
    "article_selector": "div.article-card",
    "title_selector": "h3.headline",
    "content_selector": "p.summary",
    "date_selector": "span.date",
    "link_selector": "a.article-link"
  }
}
```

**Blog/RSS:**
```json
{
  "name": "Security Blog",
  "url": "https://securityblog.com/feed",
  "enabled": true,
  "scrape_config": {
    "article_selector": "item",
    "title_selector": "title",
    "content_selector": "description",
    "date_selector": "pubDate",
    "link_selector": "link",
    "date_format": "%a, %d %b %Y %H:%M:%S %z"
  }
}
```

### Best Practices

✅ **DO:**
- Test selectors in browser first
- Use specific selectors (`.news-article` better than `div`)
- Enable only needed sources
- Set priority for important sources
- Include date format if non-standard

❌ **DON'T:**
- Use overly generic selectors (`div`, `p`)
- Enable too many sources (slows searches)
- Forget to test after adding
- Leave disabled sources (remove them)

---

## Performance Tuning

### Scraping Performance

```bash
# Scraping Settings
SCRAPER_TIMEOUT=30             # Timeout per source (seconds)
SCRAPER_MAX_RETRIES=3          # Retry failed requests
SCRAPER_DELAY=1                # Delay between requests (seconds)
MAX_CONCURRENT_SCRAPES=5       # Parallel scrapes
```

**For Speed:**
```bash
SCRAPER_TIMEOUT=15
SCRAPER_MAX_RETRIES=1
SCRAPER_DELAY=0
MAX_CONCURRENT_SCRAPES=10
```

**For Reliability:**
```bash
SCRAPER_TIMEOUT=60
SCRAPER_MAX_RETRIES=5
SCRAPER_DELAY=2
MAX_CONCURRENT_SCRAPES=3
```

### NLP Performance

```bash
# NLP Settings
NLP_MODEL=en_core_web_sm       # spaCy model (sm/md/lg)
NLP_BATCH_SIZE=50              # Process in batches
ENABLE_NER=true                # Named Entity Recognition
```

**Model Comparison:**

| Model | Size | RAM | Speed | Accuracy |
|-------|------|-----|-------|----------|
| en_core_web_sm | 12 MB | Low | Fast | Good |
| en_core_web_md | 40 MB | Medium | Medium | Better |
| en_core_web_lg | 560 MB | High | Slow | Best |

**Recommendations:**
- **Production:** `en_core_web_sm` (good balance)
- **High Accuracy:** `en_core_web_lg`
- **Resource Limited:** `en_core_web_sm`

### Query Matching

```bash
# Query Weights (must sum to ~1.0)
QUERY_WEIGHT_TITLE=0.3         # Title match importance
QUERY_WEIGHT_DESCRIPTION=0.5   # Description match importance
QUERY_WEIGHT_LOCATION=0.1      # Location match importance
QUERY_WEIGHT_TYPE=0.1          # Type match importance
```

**Tuning for Different Goals:**

**Prioritize Title Matches:**
```bash
QUERY_WEIGHT_TITLE=0.5
QUERY_WEIGHT_DESCRIPTION=0.3
QUERY_WEIGHT_LOCATION=0.1
QUERY_WEIGHT_TYPE=0.1
```

**Prioritize Description:**
```bash
QUERY_WEIGHT_TITLE=0.2
QUERY_WEIGHT_DESCRIPTION=0.6
QUERY_WEIGHT_LOCATION=0.1
QUERY_WEIGHT_TYPE=0.1
```

**Balanced:**
```bash
QUERY_WEIGHT_TITLE=0.3
QUERY_WEIGHT_DESCRIPTION=0.5
QUERY_WEIGHT_LOCATION=0.1
QUERY_WEIGHT_TYPE=0.1
```

---

## Security Configuration

### API Security

```bash
# Security
ENABLE_API_KEY=false           # Require API key
API_KEY=your-secret-key-here   # API key (if enabled)
ENABLE_RATE_LIMITING=true      # Enable rate limiting
```

**Enabling API Key Authentication:**

1. **Set in .env:**
```bash
ENABLE_API_KEY=true
API_KEY=sk_live_1234567890abcdef
```

2. **Clients must send header:**
```bash
curl -H "X-API-Key: sk_live_1234567890abcdef" \
  http://localhost:8000/search
```

3. **Frontend .env:**
```bash
VITE_API_KEY=sk_live_1234567890abcdef
```

### HTTPS/TLS

**For production, always use HTTPS.**

**Option 1: Nginx Reverse Proxy (Recommended)**
```nginx
# See DEPLOYMENT.md for full config
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
    }
}
```

**Option 2: Uvicorn with SSL**
```bash
uvicorn app.main:app \
  --ssl-keyfile=./key.pem \
  --ssl-certfile=./cert.pem
```

### Security Headers

Already configured in `main.py`:
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

---

## Logging Configuration

### Basic Settings

```bash
# Logging
LOG_LEVEL=INFO                 # Log level
LOG_DIR=logs                   # Log directory
LOG_FILE=app.log               # Log filename
LOG_MAX_BYTES=10485760         # Max size (10 MB)
LOG_BACKUP_COUNT=5             # Number of backups
LOG_FORMAT=json                # Format (json/text)
```

### Log Levels

| Level | When to Use | What's Logged |
|-------|-------------|---------------|
| DEBUG | Development | Everything (very verbose) |
| INFO | Production | Normal operations |
| WARNING | Production | Warnings & errors |
| ERROR | Minimal | Errors only |
| CRITICAL | Critical only | Critical failures |

### Log Rotation

```bash
# Rotate when file reaches size
LOG_MAX_BYTES=10485760         # 10 MB
LOG_BACKUP_COUNT=5             # Keep 5 old files

# Results in:
# logs/app.log        (current)
# logs/app.log.1      (previous)
# logs/app.log.2
# ...
# logs/app.log.5      (oldest)
```

**Recommendations:**
- **Low Traffic:** `LOG_MAX_BYTES=10485760` (10 MB), `LOG_BACKUP_COUNT=3`
- **High Traffic:** `LOG_MAX_BYTES=52428800` (50 MB), `LOG_BACKUP_COUNT=10`

### Log Format

**JSON (Recommended for production):**
```bash
LOG_FORMAT=json
```
Output:
```json
{
  "timestamp": "2025-12-02T10:30:00Z",
  "level": "INFO",
  "message": "Search completed",
  "module": "search_service"
}
```

**Text (Human-readable):**
```bash
LOG_FORMAT=text
```
Output:
```
2025-12-02 10:30:00 - INFO - search_service - Search completed
```

---

## Common Scenarios

### Scenario 1: Development Setup

```bash
# backend/.env
DEBUG=true
LOG_LEVEL=DEBUG
HOST=127.0.0.1
PORT=8000
RELOAD=true
WORKERS=1
CORS_ORIGINS=http://localhost:5173
OLLAMA_URL=http://localhost:11434
ENABLE_CACHING=false

# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_DEBUG=true
```

### Scenario 2: Production Setup (Single Server)

```bash
# backend/.env
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
RELOAD=false
WORKERS=9                      # For 4-core CPU
CORS_ORIGINS=https://events.company.com
OLLAMA_URL=http://localhost:11434
ENABLE_CACHING=true
CACHE_TTL=3600
RATE_LIMIT_SEARCH=20
SESSION_CLEANUP_HOURS=24

# frontend/.env
VITE_API_BASE_URL=https://events.company.com/api
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true
```

### Scenario 3: Production with Separate Ollama Server

```bash
# backend/.env
OLLAMA_URL=http://ollama-server.internal:11434
OLLAMA_TIMEOUT=180
OLLAMA_RETRIES=5
```

### Scenario 4: High-Performance Configuration

```bash
# backend/.env
MAX_CONCURRENT_SCRAPES=10
MAX_EVENTS_PER_ARTICLE=5
SCRAPER_TIMEOUT=15
SCRAPER_MAX_RETRIES=1
NLP_MODEL=en_core_web_sm
ENABLE_CACHING=true
CACHE_TTL=1800
WORKERS=17                     # For 8-core CPU
```

### Scenario 5: High-Accuracy Configuration

```bash
# backend/.env
MAX_CONCURRENT_SCRAPES=3
MAX_EVENTS_PER_ARTICLE=20
OLLAMA_MODEL=llama2:13b
OLLAMA_TEMPERATURE=0.0
NLP_MODEL=en_core_web_lg
ENABLE_CACHING=false
```

---

## Validation & Testing

### Test Configuration Loading

```bash
# Check if settings load correctly
cd backend
python -c "from app.settings import settings; print(settings.dict())"
```

### Test API Connection

```bash
# Health check
curl http://localhost:8000/health

# Expected:
{"status": "healthy", "timestamp": "..."}
```

### Test Ollama Connection

```bash
# Check Ollama status
curl http://localhost:8000/ollama/status

# Expected:
{"status": "connected", "model": "llama3.1:8b"}
```

### Test Sources Configuration

```bash
# List configured sources
curl http://localhost:8000/sources

# Expected:
{"sources": [...], "total": 5}
```

### Test CORS

```bash
# From browser console on frontend:
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)

# Should work without CORS errors
```

### Test Search

```bash
# Simple search test
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"phrase": "test event"}'
```

### Configuration Checklist

- [ ] `.env` files created from examples
- [ ] All required variables set
- [ ] CORS origins include frontend URL
- [ ] Ollama URL is correct
- [ ] Sources configured in `sources.json`
- [ ] Log directory exists and writable
- [ ] API key set (if enabled)
- [ ] Worker count appropriate for CPU
- [ ] Rate limits configured
- [ ] All tests pass

---

## Troubleshooting

### Configuration Not Loading

**Problem:** Changes to `.env` not taking effect

**Solutions:**
1. Restart the application
2. Check `.env` is in correct directory
3. Verify no syntax errors in `.env`
4. Check environment variable priority

### CORS Errors

**Problem:** Frontend can't connect to backend

**Solutions:**
```bash
# Check CORS_ORIGINS includes frontend URL
CORS_ORIGINS=http://localhost:5173

# For multiple origins:
CORS_ORIGINS=http://localhost:5173,https://yourdomain.com

# Check for trailing slashes (should not have them)
```

### Ollama Connection Failed

**Problem:** Can't connect to Ollama

**Solutions:**
1. Check Ollama is running: `ollama list`
2. Verify URL: `curl http://localhost:11434/api/version`
3. Check firewall if remote Ollama
4. Increase timeout if slow network

### Sources Not Working

**Problem:** No events extracted from sources

**Solutions:**
1. Verify sources.json is valid JSON
2. Test selectors in browser console
3. Check `enabled: true` for sources
4. Review logs for scraping errors
5. Test URL manually: `curl <source-url>`

---

## Additional Resources

- [Deployment Guide](DEPLOYMENT.md)
- [API Documentation](API.md)
- [User Guide](USER_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

**Last Updated:** December 2, 2025  
**Version:** 1.0.0
