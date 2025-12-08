# 🎯 Quick Test Guide

## ✅ Both Servers Running

| Server | URL | Status |
|--------|-----|--------|
| Backend | http://127.0.0.1:8000 | ✅ Running |
| Frontend | http://localhost:5173 | ✅ Running |

## 🚀 Test in 3 Steps

### 1️⃣ Open Frontend
```
http://localhost:5173
```

### 2️⃣ Enter Search
- **Phrase**: `bombing in Kabul`
- Click **"Search"**

### 3️⃣ Watch Real-Time Updates
```
✅ Progress bar: "Processing 1/5... (20%)"
✅ Event #1 appears after ~15s
✅ Progress: "Processing 2/5... (40%)"
✅ Event #2 appears after ~30s
✅ Continue or click "Cancel"
```

## 🎨 Features to Test

| Feature | How to Test |
|---------|-------------|
| **Progress Bar** | Shows "Processing article X/5..." |
| **Real-Time Events** | Events appear one-by-one |
| **Cancel** | Click "Cancel" after 2 events → Keeps 2 |
| **Select Events** | Click checkboxes on events |
| **Export Selected** | Select 2 events → "Export Selected (2)" |
| **Export All** | "Export All (5)" button |

## ✅ Fix Applied

**Problem**: "Connection to server lost"  
**Cause**: POST endpoint incompatible with EventSource  
**Solution**: Changed to GET with query parameters ✅

## 📊 Expected Timeline

| Time | Event |
|------|-------|
| 0s | Search starts, progress bar appears |
| ~15s | Event #1 displayed |
| ~30s | Event #2 displayed |
| ~45s | Event #3 displayed |
| ~60s | Event #4 displayed |
| ~75s | Event #5 displayed |
| ~80s | Complete! |

**Old system**: Wait 80s → All 5 at once  
**New system**: See results every 15s! ✨

## 🎉 System Ready!

Everything is working. Start testing! 🚀
