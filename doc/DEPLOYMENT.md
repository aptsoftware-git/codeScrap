# Event Scraper & Analyzer - Production Deployment Guide

**Version:** 1.0.0  
**Last Updated:** December 2, 2025  
**Status:** Production Ready

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Deployment](#deployment)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)
7. [Security](#security)
8. [Backup & Recovery](#backup--recovery)

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 8 GB
- Storage: 20 GB
- OS: Linux (Ubuntu 20.04+), Windows Server 2019+, macOS 11+

**Recommended:**
- CPU: 4+ cores
- RAM: 16 GB
- Storage: 50 GB SSD
- OS: Ubuntu 22.04 LTS

### Software Requirements

- **Python:** 3.10 or higher
- **Node.js:** 18 or higher
- **Ollama:** Latest version
- **Nginx:** 1.18+ (for reverse proxy)
- **Git:** For version control

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/event-scraper.git
cd event-scraper
```

### Step 2: Install Ollama

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download from: https://ollama.ai/download/windows

#### macOS
```bash
brew install ollama
```

**Pull Model:**
```bash
ollama pull llama3.1:8b
```

**Verify:**
```bash
curl http://localhost:11434
# Should return: Ollama is running
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### Step 4: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### Step 5: Configuration Files

```bash
cd ../config

# Review and update sources.yaml
nano sources.yaml
```

---

## Configuration

### Backend Configuration (.env)

**Critical Settings:**

```bash
# Production mode
DEBUG=false
LOG_LEVEL=INFO

# Server binding
HOST=0.0.0.0
PORT=8000

# CORS - Update with your frontend URL
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Security
ENABLE_SECURITY_HEADERS=true
API_KEY=your-secure-api-key-here  # Optional
```

### Frontend Configuration (.env)

```bash
# API endpoint - Update with your backend URL
VITE_API_BASE_URL=https://api.yourdomain.com

# Production settings
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true  # If using analytics
```

### Sources Configuration (config/sources.yaml)

```yaml
sources:
  - name: "News Source 1"
    base_url: "https://example.com"
    enabled: true
    category: "general"
    selectors:
      title: "h1.article-title"
      content: "div.article-content"
      date: "time.published-date"
```

---

## Deployment

### Option 1: Systemd Services (Linux)

#### Backend Service

Create `/etc/systemd/system/event-scraper-backend.service`:

```ini
[Unit]
Description=Event Scraper Backend API
After=network.target ollama.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/event-scraper/backend
Environment="PATH=/opt/event-scraper/backend/venv/bin"
ExecStart=/opt/event-scraper/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable event-scraper-backend
sudo systemctl start event-scraper-backend
sudo systemctl status event-scraper-backend
```

#### Frontend Service (Build and Serve)

**Build frontend:**
```bash
cd frontend
npm run build
```

Create `/etc/systemd/system/event-scraper-frontend.service`:

```ini
[Unit]
Description=Event Scraper Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/event-scraper/frontend
ExecStart=/usr/bin/npx serve -s dist -l 5173
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable event-scraper-frontend
sudo systemctl start event-scraper-frontend
```

### Option 2: Docker Deployment

#### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    env_file:
      - ./backend/.env
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**Run:**
```bash
docker-compose up -d
```

### Option 3: Nginx Reverse Proxy

Create `/etc/nginx/sites-available/event-scraper`:

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout for long-running scrapes
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /opt/event-scraper/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable and reload:**
```bash
sudo ln -s /etc/nginx/sites-available/event-scraper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

---

## Monitoring

### Logs

**Backend logs:**
```bash
tail -f /opt/event-scraper/backend/logs/app.log
```

**System service logs:**
```bash
sudo journalctl -u event-scraper-backend -f
sudo journalctl -u event-scraper-frontend -f
```

### Health Checks

**Backend health:**
```bash
curl http://localhost:8000/api/v1/health
```

**Ollama status:**
```bash
curl http://localhost:8000/api/v1/ollama/status
```

### Performance Monitoring

Consider using:
- **Prometheus** + **Grafana** for metrics
- **Sentry** for error tracking
- **Uptime Robot** for uptime monitoring

---

## Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
sudo journalctl -u event-scraper-backend -n 50
```

**Common issues:**
1. **Ollama not running:**
   ```bash
   sudo systemctl status ollama
   sudo systemctl start ollama
   ```

2. **Port already in use:**
   ```bash
   sudo lsof -i :8000
   # Kill process or change port in .env
   ```

3. **Permission issues:**
   ```bash
   sudo chown -R www-data:www-data /opt/event-scraper
   ```

### Frontend Not Loading

**Check build:**
```bash
cd frontend
npm run build
# Check for errors
```

**Nginx errors:**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### CORS Errors

**Update backend .env:**
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Restart backend:**
```bash
sudo systemctl restart event-scraper-backend
```

### Slow Searches

1. **Check Ollama:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Reduce concurrent scrapes:**
   ```bash
   # In .env
   MAX_CONCURRENT_SCRAPES=3
   ```

3. **Use lighter model:**
   ```bash
   OLLAMA_MODEL=llama3.2:3b
   ```

---

## Security

### Best Practices

1. **Use HTTPS only in production**
2. **Set strong API keys** (if using)
3. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   npm outdated
   ```

4. **Enable security headers** in .env:
   ```bash
   ENABLE_SECURITY_HEADERS=true
   ```

5. **Restrict CORS** to known domains only

6. **Regular backups** of configuration and data

7. **Monitor logs** for suspicious activity

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

---

## Backup & Recovery

### Configuration Backup

```bash
# Backup configuration
tar -czf event-scraper-config-$(date +%Y%m%d).tar.gz \
  config/ \
  backend/.env \
  frontend/.env

# Restore
tar -xzf event-scraper-config-20251202.tar.gz
```

### Log Rotation

Edit `/etc/logrotate.d/event-scraper`:

```
/opt/event-scraper/backend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload event-scraper-backend > /dev/null 2>&1 || true
    endscript
}
```

---

## Performance Tuning

### Backend Optimization

**Use Gunicorn with multiple workers:**

```bash
pip install gunicorn

# Run with 4 workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Update systemd service:**
```ini
ExecStart=/opt/event-scraper/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Ollama Optimization

**Enable GPU acceleration** (if available):
```bash
# NVIDIA GPU
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

---

## Production Checklist

Before going live:

- [ ] All .env files configured correctly
- [ ] HTTPS enabled with valid certificates
- [ ] CORS restricted to production domains
- [ ] Security headers enabled
- [ ] Firewall configured
- [ ] Monitoring set up
- [ ] Log rotation configured
- [ ] Backup strategy in place
- [ ] Health checks working
- [ ] Load testing completed
- [ ] Documentation reviewed
- [ ] Admin contacts updated

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/event-scraper/issues
- Documentation: https://github.com/yourusername/event-scraper/wiki
- Email: support@yourdomain.com

---

**End of Deployment Guide**
