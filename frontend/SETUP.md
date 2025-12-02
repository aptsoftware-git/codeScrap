# Event Scraper & Analyzer - Frontend Setup Guide

**Version**: 1.0  
**Last Updated**: December 2, 2025  
**Status**: Production Ready

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Backend Connection](#backend-connection)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Production Build](#production-build)

---

## Prerequisites

### Required Software

- **Node.js**: 18.19.1 or higher (tested with 18.19.1)
- **npm**: 10.5.0 or higher
- **Backend API**: Running on http://127.0.0.1:8000 (or http://localhost:8000)
- **Modern Browser**: Chrome, Firefox, Safari, or Edge (latest versions)

### Check Your Versions

```powershell
# Check Node.js version
node --version
# Should show: v18.19.1 or higher

# Check npm version
npm --version
# Should show: 10.5.0 or higher
```

---

## Installation

### Step 1: Navigate to Frontend Directory

```powershell
cd C:\Anu\APT\apt\defender\scraping\code\frontend
```

### Step 2: Install Dependencies

```powershell
npm install
```

This will install all required packages:
- React 18.2.0
- TypeScript 5.0.2
- Material-UI 7.3.5
- Axios 1.13.2
- Vite 4.5.14
- And all other dependencies

**Installation Time**: ~2-3 minutes (depending on internet speed)

**Expected Output**:
```
added 199 packages, and audited 200 packages in 19s
42 packages are looking for funding
```

### Step 3: Verify Installation

```powershell
# Check installed packages
npm list --depth=0
```

You should see all dependencies listed without errors.

---

## Configuration

### Backend API URL

The frontend is pre-configured to connect to the backend at:
```
http://localhost:8000
```

#### To Change Backend URL

If your backend runs on a different URL, edit:

**File**: `src/services/api.ts`

```typescript
// Line 10
constructor(baseURL: string = 'http://localhost:8000') {
  // Change to your backend URL:
  // constructor(baseURL: string = 'http://your-backend:port') {
  this.client = axios.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 120000, // 2 minutes
  });
}
```

**Common Backend URLs**:
- Local development: `http://localhost:8000`
- Local IP: `http://127.0.0.1:8000`
- Remote server: `http://your-server-ip:8000`
- Production: `https://api.your-domain.com`

---

## Running the Application

### Start Development Server

```powershell
# Make sure you're in the frontend directory
cd C:\Anu\APT\apt\defender\scraping\code\frontend

# Start the dev server
npm run dev
```

**Expected Output**:
```
  VITE v4.5.14  ready in 453 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

The application should load with:
- Blue app bar: "Event Scraper & Analyzer"
- Search form with input fields
- Clean, professional Material-UI interface

### Stop the Server

Press `Ctrl + C` in the terminal where the dev server is running.

---

## Backend Connection

### Prerequisites

The frontend requires the backend API to be running. The backend provides:
- Event search functionality
- Session management
- Excel export generation

### Start Backend Server

**In a separate terminal** (not the frontend terminal):

```powershell
# Navigate to backend directory
cd C:\Anu\APT\apt\defender\scraping\code\backend

# Activate virtual environment (if using venv)
.\venv\Scripts\Activate

# Start backend server
uvicorn app.main:app --reload
```

**Expected Backend Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Verify Backend Connection

**Option 1: Browser**
Open: http://127.0.0.1:8000/docs

You should see the FastAPI Swagger documentation.

**Option 2: Command Line**
```powershell
# Test health endpoint
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

### CORS Configuration

The backend must allow requests from the frontend URL.

**Backend CORS Configuration** (should already be set):

```python
# In backend/app/main.py

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Frontend dev server
        "http://127.0.0.1:5173",  # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For Production**: Add your production domain to `allow_origins`.

---

## Testing

### Quick Functionality Test

1. **Open Frontend**: http://localhost:5173
2. **Enter Search Query**: `"AI conference"`
3. **Click "Search"**
4. **Wait**: 30-60 seconds (normal for scraping and analysis)
5. **Verify**: Results appear as event cards

### Detailed Testing

See comprehensive testing guides in the `test/` directory:

- **`test/QUICKSTART_TEST.md`** - 5-minute quick test
- **`test/TESTING_GUIDE.md`** - Complete testing procedures
- **`test/TEST_RESULTS.md`** - Test execution template

### Check Browser Console

1. Open browser DevTools (F12)
2. Go to Console tab
3. **Verify**:
   - ✅ No error messages (red text)
   - ✅ No CORS errors
   - ✅ No 404 errors

### Check Network Requests

1. Open DevTools (F12) → Network tab
2. Perform a search
3. **Verify**:
   - ✅ POST request to `/api/v1/search`
   - ✅ Status: 200 OK
   - ✅ Response contains events array

---

## Troubleshooting

### Issue: npm install fails

**Error**: `npm ERR! network timeout`

**Solution**:
```powershell
# Clear npm cache
npm cache clean --force

# Try again
npm install
```

---

### Issue: Port 5173 already in use

**Error**: `Port 5173 is already in use`

**Solution 1**: Stop the other process using the port

**Solution 2**: Use a different port
```powershell
# Edit package.json, add --port flag
# Or set in vite.config.ts
```

---

### Issue: Cannot connect to backend

**Error**: `Network Error` or `ERR_CONNECTION_REFUSED`

**Checklist**:
1. ✅ Backend server is running (`uvicorn app.main:app --reload`)
2. ✅ Backend is on http://127.0.0.1:8000
3. ✅ Test: `curl http://127.0.0.1:8000/api/v1/health`
4. ✅ Check backend terminal for errors

---

### Issue: CORS Error

**Error**: `Access to XMLHttpRequest has been blocked by CORS policy`

**Solution**: 
Verify backend has CORS middleware configured for `http://localhost:5173`.

See [Backend Connection](#backend-connection) section above.

---

### Issue: Blank page after npm run dev

**Checklist**:
1. ✅ Check browser console for errors (F12)
2. ✅ Verify URL is http://localhost:5173
3. ✅ Check terminal for compilation errors
4. ✅ Try hard refresh: `Ctrl + Shift + R`

---

### Issue: Search takes too long (>2 minutes)

**Expected**: 30-60 seconds is normal

**If longer**:
1. Check backend logs for errors
2. Verify Ollama is running (backend dependency)
3. Check network connection
4. Some news sources may be slow (normal)

---

### Issue: No search results

**Possible Causes**:
1. No articles matched the query
2. Try broader search terms: `"conference"` instead of specific names
3. Remove filters (location, event type, dates)
4. Check backend logs for scraping errors

---

### Issue: TypeScript errors

**Error**: `Cannot find module` or type errors

**Solution**:
```powershell
# Reinstall dependencies
rm -r node_modules package-lock.json
npm install

# Restart dev server
npm run dev
```

---

## Production Build

### Build for Production

```powershell
# Create optimized production build
npm run build
```

**Output**: `dist/` directory with optimized files

**Build Time**: ~10-15 seconds

### Preview Production Build

```powershell
# Preview the production build locally
npm run preview
```

Opens on: http://localhost:4173

### Deploy Production Build

The `dist/` directory contains all files needed for deployment.

**Deployment Options**:
1. **Static hosting**: Netlify, Vercel, GitHub Pages
2. **Web server**: Apache, Nginx
3. **Cloud**: AWS S3, Azure Static Web Apps

**Example: Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy API requests to backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Environment Variables

### Create .env File (Optional)

For different environments, create `.env` files:

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000

# .env.production
VITE_API_BASE_URL=https://api.your-domain.com
```

### Use in Code

Update `src/services/api.ts`:

```typescript
constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') {
  // Uses env variable if available, falls back to default
}
```

---

## Quick Reference Commands

```powershell
# Installation
npm install

# Development server
npm run dev

# Production build
npm run build

# Preview production
npm run preview

# Type checking
npm run lint

# Clean install
rm -r node_modules package-lock.json && npm install
```

---

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── SearchForm.tsx   # Main search form
│   │   ├── EventList.tsx    # Results list
│   │   └── EventCard.tsx    # Event card display
│   ├── services/
│   │   └── api.ts           # Backend API client
│   ├── types/
│   │   └── events.ts        # TypeScript definitions
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   ├── App.css              # Styles
│   └── index.css            # Global styles
├── public/                  # Static assets
├── doc/                     # Documentation
│   ├── QUICKSTART_TEST.md
│   ├── TESTING_GUIDE.md
│   ├── TEST_RESULTS.md
│   ├── INCREMENT9_COMPLETE.md
│   └── REVIEW_INCREMENT9.md
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── vite.config.ts           # Vite config
├── README.md                # Project overview
└── SETUP.md                 # This file
```

---

## System Requirements

### Minimum Requirements

- **OS**: Windows 10+, macOS 10.15+, Linux
- **RAM**: 4GB
- **Node.js**: 18.x
- **Browser**: Modern browser (last 2 versions)
- **Internet**: Required for npm install and API calls

### Recommended Requirements

- **RAM**: 8GB+
- **Node.js**: 18.19.1 or latest LTS
- **SSD**: For faster development
- **Internet**: Stable connection for scraping

---

## Development Workflow

### Typical Development Session

```powershell
# 1. Start backend (separate terminal)
cd backend
.\venv\Scripts\Activate
uvicorn app.main:app --reload

# 2. Start frontend (separate terminal)
cd frontend
npm run dev

# 3. Open browser
# Navigate to http://localhost:5173

# 4. Make changes
# Vite will auto-reload on file save

# 5. Test changes
# Use browser and backend integration

# 6. When done, stop servers
# Ctrl + C in both terminals
```

---

## Getting Help

### Documentation

- **README.md** - Project overview and features
- **SETUP.md** - This file (installation and setup)
- **test/QUICKSTART_TEST.md** - Quick testing guide
- **test/TESTING_GUIDE.md** - Comprehensive testing
- **doc/INCREMENT9_COMPLETE.md** - Implementation details
- **doc/REVIEW_INCREMENT9.md** - Code review

### Common Issues

Check [Troubleshooting](#troubleshooting) section above.

### Backend Documentation

See: `../backend/README.md`

### Check Logs

**Frontend**: Browser console (F12 → Console)  
**Backend**: Terminal where uvicorn is running

---

## Success Checklist

Before considering setup complete, verify:

- [ ] Node.js 18+ installed
- [ ] npm install completed without errors
- [ ] npm run dev starts successfully
- [ ] Frontend loads at http://localhost:5173
- [ ] Backend running at http://127.0.0.1:8000
- [ ] Backend health check passes
- [ ] No CORS errors in console
- [ ] Sample search returns results
- [ ] Sorting works
- [ ] Excel export works
- [ ] No errors in browser console

---

## Next Steps

After successful setup:

1. ✅ Run through quick test (5 minutes) - see `test/QUICKSTART_TEST.md`
2. ✅ Perform full testing (20 minutes) - see `test/TESTING_GUIDE.md`
3. ✅ Customize for your needs
4. ✅ Deploy to production (when ready)

---

## Version History

- **1.0** (Dec 2, 2025) - Initial setup guide
  - Complete installation instructions
  - Backend connection guide
  - Troubleshooting section
  - Production build guide

---

**Setup Status**: ✅ **COMPLETE**  
**Ready for**: Development, Testing, Production

**Questions?** Check the documentation in the `doc/` directory.

---

**End of Setup Guide**
