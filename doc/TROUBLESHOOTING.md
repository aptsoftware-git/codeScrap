# Troubleshooting Guide

This guide helps you diagnose and fix common issues with the Event Scraper & Analyzer.

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Backend Issues](#backend-issues)
4. [Frontend Issues](#frontend-issues)
5. [Ollama Issues](#ollama-issues)
6. [Scraping Issues](#scraping-issues)
7. [Performance Issues](#performance-issues)
8. [Data Quality Issues](#data-quality-issues)
9. [Export Issues](#export-issues)
10. [Deployment Issues](#deployment-issues)

---

## Quick Diagnostics

### System Health Check

Run these commands to check system status:

```bash
# 1. Check backend status
curl http://localhost:8000/health

# 2. Check Ollama connection
curl http://localhost:8000/ollama/status

# 3. Check sources
curl http://localhost:8000/sources

# 4. Check frontend
# Open browser to: http://localhost:5173
```

### Expected Results

**Healthy System:**
```json
// /health
{"status": "healthy", "timestamp": "2025-12-02T10:30:00Z"}

// /ollama/status
{"status": "connected", "model": "llama3.1:8b", "version": "..."}

// /sources
{"sources": [...], "total": 5, "enabled": 5}
```

**Frontend:**
- Page loads without errors
- Search form is visible
- No console errors (F12)

### Check Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Check for errors
grep -i error backend/logs/app.log

# Check recent activity
tail -n 100 backend/logs/app.log
```

---

## Installation Issues

### Issue: Python Version Mismatch

**Symptoms:**
- `python` command not found
- Wrong Python version

**Diagnosis:**
```bash
python --version
# or
python3 --version
```

**Solution:**
```bash
# Install Python 3.8+
# Ubuntu/Debian:
sudo apt update
sudo apt install python3.11 python3.11-venv

# Windows:
# Download from python.org

# macOS:
brew install python@3.11
```

### Issue: pip Install Failures

**Symptoms:**
- `pip install` fails
- Dependency conflicts
- Permission errors

**Solution 1: Use virtual environment**
```bash
cd backend
python -m venv venv

# Activate
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install
pip install -r requirements.txt
```

**Solution 2: Upgrade pip**
```bash
pip install --upgrade pip setuptools wheel
```

**Solution 3: Permission issues (Linux)**
```bash
# Don't use sudo pip!
# Use --user flag:
pip install --user -r requirements.txt

# Or use venv (recommended)
```

**Solution 4: Dependency conflicts**
```bash
# Clear cache and retry
pip cache purge
pip install --no-cache-dir -r requirements.txt

# Try compatible versions
pip install -r requirements-py38.txt
```

### Issue: Ollama Installation Failed

**Symptoms:**
- `ollama: command not found`
- Can't download models

**Solutions:**

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh

# Check installation
ollama --version
```

**Windows:**
```powershell
# Download from https://ollama.com/download
# Run installer
```

**macOS:**
```bash
brew install ollama

# Or download from https://ollama.com/download
```

### Issue: npm Install Failures

**Symptoms:**
- `npm install` fails in frontend
- Module not found errors

**Solution:**
```bash
cd frontend

# Clear cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install

# If still fails, use specific version
npm install --legacy-peer-deps
```

---

## Backend Issues

### Issue: Backend Won't Start

**Symptoms:**
- `uvicorn` command fails
- Port already in use
- Import errors

**Diagnosis:**
```bash
# Check if port 8000 is in use
# Linux/macOS:
lsof -i :8000
# Windows:
netstat -ano | findstr :8000

# Try starting with verbose output
cd backend
python -m uvicorn app.main:app --reload
```

**Solutions:**

**Port in use:**
```bash
# Kill existing process
# Linux/macOS:
kill -9 $(lsof -t -i:8000)
# Windows:
# Note the PID from netstat, then:
taskkill /PID <pid> /F

# Or use different port
uvicorn app.main:app --port 8001
```

**Import errors:**
```bash
# Check you're in correct directory
pwd  # Should be in backend/

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

**Module not found:**
```bash
# Install missing module
pip install <module-name>

# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

### Issue: 500 Internal Server Error

**Symptoms:**
- API returns 500 errors
- Crashes on requests

**Diagnosis:**
```bash
# Check logs
tail -f backend/logs/app.log

# Test specific endpoint
curl -v http://localhost:8000/health
```

**Solutions:**

**Check logs for error:**
```bash
# Find the error
grep -A 10 "ERROR" backend/logs/app.log

# Common errors:
# 1. Database connection failed
# 2. Ollama not responding
# 3. Invalid configuration
# 4. Missing dependencies
```

**Test components individually:**
```bash
# Test Ollama
curl http://localhost:11434/api/version

# Test sources
python -c "import json; print(json.load(open('config/sources.json')))"

# Test settings
cd backend
python -c "from app.settings import settings; print(settings.dict())"
```

### Issue: CORS Errors

**Symptoms:**
- Browser console: "CORS policy blocked"
- Frontend can't connect to backend

**Diagnosis:**
```bash
# Check browser console (F12)
# Look for errors like:
# "Access to fetch at 'http://localhost:8000' from origin 
# 'http://localhost:5173' has been blocked by CORS policy"
```

**Solutions:**

**Fix CORS configuration:**
```bash
# Edit backend/.env
CORS_ORIGINS=http://localhost:5173

# For multiple origins (comma-separated, no spaces):
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Restart backend
```

**Verify CORS headers:**
```bash
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     -v \
     http://localhost:8000/search

# Should see:
# Access-Control-Allow-Origin: http://localhost:5173
```

### Issue: Rate Limiting

**Symptoms:**
- "Rate limit exceeded" error
- 429 Too Many Requests

**Solution:**
```bash
# Edit backend/.env
# Increase limits:
RATE_LIMIT_SEARCH=20
RATE_LIMIT_EXPORT=10

# Or disable:
RATE_LIMIT_SEARCH=1000
RATE_LIMIT_EXPORT=1000

# Restart backend
```

---

## Frontend Issues

### Issue: Frontend Won't Start

**Symptoms:**
- `npm run dev` fails
- Blank page
- Module errors

**Diagnosis:**
```bash
cd frontend

# Check for errors
npm run dev

# Check Node version
node --version  # Should be 16+
```

**Solutions:**

**Node version too old:**
```bash
# Install Node 16+
# Using nvm (recommended):
nvm install 18
nvm use 18

# Verify
node --version
```

**Dependencies missing:**
```bash
# Reinstall
rm -rf node_modules package-lock.json
npm install
```

**Port 5173 in use:**
```bash
# Use different port
npm run dev -- --port 5174

# Or kill existing process
# Linux/macOS:
lsof -t -i:5173 | xargs kill -9
# Windows:
netstat -ano | findstr :5173
taskkill /PID <pid> /F
```

### Issue: Blank Page / White Screen

**Symptoms:**
- Page loads but nothing displays
- No errors in console

**Diagnosis:**
```bash
# Open browser console (F12)
# Check for errors

# Check network tab
# Look for failed requests
```

**Solutions:**

**Check API connection:**
```bash
# Verify frontend/.env
VITE_API_BASE_URL=http://localhost:8000

# Test from browser console:
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
```

**Clear browser cache:**
```
Ctrl+Shift+Delete (Windows/Linux)
Cmd+Shift+Delete (macOS)
```

**Rebuild frontend:**
```bash
cd frontend
rm -rf node_modules dist
npm install
npm run dev
```

### Issue: Search Button Not Working

**Symptoms:**
- Click search, nothing happens
- No results displayed
- No errors

**Diagnosis:**
```bash
# Open browser console (F12)
# Click search
# Check for errors

# Check network tab
# Look for /search request
```

**Solutions:**

**Check API URL:**
```bash
# Verify in frontend/.env
VITE_API_BASE_URL=http://localhost:8000

# Test manually:
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"phrase": "test"}'
```

**Check form validation:**
```
# Error: "Please enter a search phrase"
# → Enter text in search box

# Error: "Start date must be before end date"
# → Fix date range
```

**Check backend logs:**
```bash
tail -f backend/logs/app.log
# Click search on frontend
# Watch for errors
```

---

## Ollama Issues

### Issue: Ollama Not Running

**Symptoms:**
- "Failed to connect to Ollama"
- 500 error on search

**Diagnosis:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Check process
# Linux/macOS:
ps aux | grep ollama
# Windows:
tasklist | findstr ollama
```

**Solutions:**

**Start Ollama:**
```bash
# Linux/macOS:
ollama serve

# Windows:
# Start from Start Menu or:
ollama serve

# Run in background (Linux):
nohup ollama serve > /dev/null 2>&1 &
```

**Enable as service (Linux):**
```bash
# See DEPLOYMENT.md for systemd service setup
sudo systemctl start ollama
sudo systemctl enable ollama
```

### Issue: Model Not Found

**Symptoms:**
- "Model 'llama3.1:8b' not found"
- Ollama running but search fails

**Diagnosis:**
```bash
# List installed models
ollama list
```

**Solution:**
```bash
# Download model
ollama pull llama3.1:8b

# For other models:
ollama pull llama2:13b
ollama pull mistral:7b

# Verify
ollama list
```

### Issue: Ollama Slow/Timeout

**Symptoms:**
- Search takes >2 minutes
- Timeout errors
- "Ollama request timed out"

**Solutions:**

**Increase timeout:**
```bash
# Edit backend/.env
OLLAMA_TIMEOUT=300  # 5 minutes

# Restart backend
```

**Use smaller model:**
```bash
# Switch to faster model
OLLAMA_MODEL=mistral:7b

# Or smaller version
OLLAMA_MODEL=llama3.1:8b  # Instead of 13b/70b
```

**Check GPU acceleration:**
```bash
# Check if GPU is being used
nvidia-smi  # For NVIDIA GPUs

# If not using GPU, install CUDA toolkit
# See Ollama documentation
```

**Reduce context window:**
```bash
# Edit backend/.env
OLLAMA_NUM_CTX=2048  # Instead of 4096
OLLAMA_NUM_PREDICT=512  # Instead of 1024
```

### Issue: Out of Memory

**Symptoms:**
- Ollama crashes
- "Out of memory" errors
- System freezes during search

**Solutions:**

**Use smaller model:**
```bash
# 8b models: ~16GB RAM
# 13b models: ~24GB RAM
# 70b models: ~64GB RAM

# Switch to smaller:
ollama pull llama3.1:8b
OLLAMA_MODEL=llama3.1:8b
```

**Limit concurrent operations:**
```bash
# Edit backend/.env
MAX_CONCURRENT_SCRAPES=1
OLLAMA_NUM_CTX=2048
```

**Close other applications:**
```bash
# Free up RAM before searching
```

---

## Scraping Issues

### Issue: No Articles Scraped

**Symptoms:**
- Search returns 0 results
- "No events found"
- sources.json configured

**Diagnosis:**
```bash
# Check sources
curl http://localhost:8000/sources

# Check logs during search
tail -f backend/logs/app.log

# Test source manually
curl <source-url>
```

**Solutions:**

**Verify sources configuration:**
```bash
# Check config/sources.json is valid
python -c "import json; print(json.load(open('config/sources.json')))"

# Verify selectors work
# Open source URL in browser
# Use DevTools (F12) to test selectors
document.querySelectorAll('article.news-item')
```

**Enable sources:**
```json
// In config/sources.json
{
  "enabled": true  // Must be true!
}
```

**Check network connectivity:**
```bash
# Test reaching source
curl -v <source-url>

# Check firewall/proxy
```

### Issue: Incorrect/Incomplete Data

**Symptoms:**
- Missing titles/dates/descriptions
- Garbled text
- Wrong data in fields

**Solutions:**

**Update CSS selectors:**
```json
// In config/sources.json
// Inspect website to find correct selectors
{
  "scrape_config": {
    "article_selector": "div.article",  // Update these
    "title_selector": "h2.title",
    "content_selector": "p.summary",
    "date_selector": "time",
    "link_selector": "a.link"
  }
}
```

**Test selectors:**
```javascript
// In browser console on source website:
document.querySelectorAll('div.article')
document.querySelector('h2.title')?.textContent
```

**Check date format:**
```json
// Add date format if non-standard:
{
  "scrape_config": {
    "date_format": "%Y-%m-%d"
  }
}
```

### Issue: Website Blocking Scraper

**Symptoms:**
- 403 Forbidden errors
- 429 Too Many Requests
- Captcha pages

**Solutions:**

**Add delays:**
```bash
# Edit backend/.env
SCRAPER_DELAY=2  # Wait 2 seconds between requests
```

**Change user agent:**
```bash
# Edit backend/.env
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

**Respect robots.txt:**
```bash
# Check if scraping is allowed
curl https://example.com/robots.txt
```

**Use API instead:**
```
# Many sites offer APIs
# Use their API instead of scraping
```

---

## Performance Issues

### Issue: Slow Searches

**Symptoms:**
- Searches take >60 seconds
- System freezes
- High CPU/RAM usage

**Diagnosis:**
```bash
# Check system resources
top  # Linux/macOS
# Task Manager on Windows

# Check which component is slow
# Look at logs for timing
```

**Solutions:**

**Reduce concurrent operations:**
```bash
# Edit backend/.env
MAX_CONCURRENT_SCRAPES=3  # Instead of 10
```

**Limit sources:**
```json
// In config/sources.json
// Disable slow sources
{
  "enabled": false
}
```

**Use smaller model:**
```bash
OLLAMA_MODEL=mistral:7b
NLP_MODEL=en_core_web_sm
```

**Enable caching:**
```bash
ENABLE_CACHING=true
CACHE_TTL=3600
```

**Limit events per article:**
```bash
MAX_EVENTS_PER_ARTICLE=5  # Instead of 10
```

### Issue: High Memory Usage

**Symptoms:**
- RAM usage keeps increasing
- System swap usage high
- Out of memory errors

**Solutions:**

**Restart application:**
```bash
# Memory leaks may occur
# Restart periodically:
sudo systemctl restart event-scraper
```

**Reduce batch size:**
```bash
NLP_BATCH_SIZE=25  # Instead of 50
```

**Use smaller model:**
```bash
OLLAMA_MODEL=llama3.1:8b  # Not 13b/70b
NLP_MODEL=en_core_web_sm  # Not lg
```

**Limit workers:**
```bash
WORKERS=4  # Instead of (2 * cores + 1)
```

---

## Data Quality Issues

### Issue: Irrelevant Results

**Symptoms:**
- Results don't match query
- Low relevance scores
- Wrong event types

**Solutions:**

**Use more specific phrases:**
```
❌ "attack"
✅ "cyber attack on financial institutions"
```

**Add filters:**
```
Use:
- Event Type filter
- Location filter
- Date range
```

**Adjust query weights:**
```bash
# Edit backend/.env
# Prioritize title over description:
QUERY_WEIGHT_TITLE=0.5
QUERY_WEIGHT_DESCRIPTION=0.3
```

**Improve prompts:**
```python
# In ollama_service.py
# Adjust extraction prompts for better results
```

### Issue: Missing Events

**Symptoms:**
- Know event exists but not found
- Incomplete results

**Solutions:**

**Broaden search:**
```
- Use synonyms
- Remove filters
- Expand date range
```

**Check if source has event:**
```bash
# Manually visit source website
# Verify event is published
```

**Add more sources:**
```json
// In config/sources.json
// Add relevant news sources
```

**Increase max events:**
```bash
MAX_EVENTS_PER_ARTICLE=20  # Instead of 10
```

### Issue: Duplicate Events

**Symptoms:**
- Same event appears multiple times
- Different sources, same story

**Note:**
This is expected when multiple sources cover the same event.

**Solutions:**

**Filter after export:**
```
# In Excel:
# Remove duplicates by title/date/location
```

**Prefer primary sources:**
```json
// In config/sources.json
// Set higher priority for primary sources
{
  "priority": 1
}
```

---

## Export Issues

### Issue: Export Fails

**Symptoms:**
- "Export failed" message
- No file downloaded
- 500 error

**Diagnosis:**
```bash
# Check backend logs
tail -f backend/logs/app.log

# Try export API directly
curl -X POST http://localhost:8000/export/excel \
  -H "Content-Type: application/json" \
  -d '{"session_id": "..."}'
```

**Solutions:**

**Check session exists:**
```bash
# Session might have expired
# Try new search first
```

**Check disk space:**
```bash
df -h  # Linux/macOS
# Windows: Check in Explorer
```

**Check write permissions:**
```bash
# Backend needs write access to temp directory
chmod 777 /tmp  # Linux/macOS (not recommended for production)
```

### Issue: Excel File Corrupted

**Symptoms:**
- Can't open file
- "File is corrupted" error
- Data missing in file

**Solutions:**

**Try different export:**
```
# Export fewer events
# Select specific events instead of all
```

**Check Excel version:**
```
# File uses .xlsx format
# Requires Excel 2007+ or compatible
```

**Try LibreOffice/Google Sheets:**
```
# May have better compatibility
```

### Issue: Export Too Large

**Symptoms:**
- Export takes forever
- File very large (>50 MB)
- Excel crashes opening file

**Solutions:**

**Export in batches:**
```
# Select 100-200 events at a time
# Export multiple files
```

**Filter results first:**
```
# Use date range
# Use event type filter
# Use location filter
```

**Increase limit:**
```bash
# Edit frontend/.env
VITE_MAX_EXPORT_EVENTS=500  # Instead of 1000
```

---

## Deployment Issues

### Issue: systemd Service Won't Start

**Symptoms:**
- `systemctl start` fails
- Service shows "failed" status

**Diagnosis:**
```bash
# Check service status
sudo systemctl status event-scraper

# Check logs
sudo journalctl -u event-scraper -n 50

# Test manually
su - scraper-user
cd /opt/event-scraper/backend
source venv/bin/activate
uvicorn app.main:app
```

**Solutions:**

**Fix service file:**
```bash
# Edit /etc/systemd/system/event-scraper.service
# Verify paths are correct:
# - WorkingDirectory
# - ExecStart
# - User

# Reload systemd
sudo systemctl daemon-reload

# Retry
sudo systemctl start event-scraper
```

**Check permissions:**
```bash
# Service user must own files
sudo chown -R scraper-user:scraper-user /opt/event-scraper
```

**Check environment:**
```bash
# .env file must exist
ls -la /opt/event-scraper/backend/.env

# Test loading environment
cd /opt/event-scraper/backend
source venv/bin/activate
python -c "from app.settings import settings; print(settings.dict())"
```

### Issue: Nginx Reverse Proxy Not Working

**Symptoms:**
- 502 Bad Gateway
- Can't reach backend through domain
- Direct access works, proxy doesn't

**Diagnosis:**
```bash
# Check Nginx config
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Check backend is running
curl http://127.0.0.1:8000/health
```

**Solutions:**

**Fix Nginx config:**
```nginx
# /etc/nginx/sites-available/event-scraper
# Verify backend URL
location /api {
    proxy_pass http://127.0.0.1:8000;  # Correct port
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/event-scraper \
           /etc/nginx/sites-enabled/

sudo nginx -t
sudo systemctl reload nginx
```

**Check firewall:**
```bash
# Allow Nginx
sudo ufw allow 'Nginx Full'

# Or specific ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Issue: Docker Container Crashes

**Symptoms:**
- Container exits immediately
- `docker ps` shows no containers

**Diagnosis:**
```bash
# Check container logs
docker logs event-scraper-backend

# Check if container exists
docker ps -a
```

**Solutions:**

**Restart container:**
```bash
docker-compose restart
```

**Rebuild image:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Check environment:**
```bash
# Verify docker-compose.yml has correct env files
env_file:
  - ./backend/.env
```

**Check volumes:**
```bash
# Ensure volumes exist
docker volume ls

# Recreate if needed
docker-compose down -v
docker-compose up -d
```

---

## Getting More Help

### Collect Debug Information

```bash
# System info
uname -a  # Linux/macOS
systeminfo  # Windows

# Python version
python --version

# Node version
node --version

# Ollama version
ollama --version

# Backend logs
tail -n 100 backend/logs/app.log > debug-backend.log

# Frontend errors
# From browser console (F12), copy errors

# Configuration (remove sensitive data!)
cat backend/.env | grep -v "API_KEY"
```

### Contact Support

**Email:** support@yourdomain.com

**Include:**
1. What you were trying to do
2. What actually happened
3. Error messages
4. Debug information (above)
5. Screenshots (if helpful)

### Report Bugs

**GitHub Issues:** https://github.com/yourorg/event-scraper/issues

**Bug Report Template:**
```markdown
## Description
Brief description of the issue

## Steps to Reproduce
1. Step 1
2. Step 2
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: 
- Python version:
- Node version:
- Ollama version:

## Logs
```
Paste relevant log snippets here
```

## Screenshots
(if applicable)
```

---

**Last Updated:** December 2, 2025  
**Version:** 1.0.0
