# 🔧 Ollama Optimization for 16GB RAM System

## 🖥️ Your System Specs
- **CPU**: Intel i7-1065G7 (4 cores, 8 threads)
- **RAM**: 16GB (15.8GB available)
- **OS**: Windows 11 Home

## ❌ Problem
Ollama hangs the machine when processing multiple articles simultaneously.

## ✅ Solution Applied

### **1. Backend Configuration Updated** (`backend/.env`)

**Changed Settings**:
```properties
# OLD (Server-grade configuration)
MAX_CONCURRENT_SCRAPES=10    # Too many parallel scrapes
MAX_CONCURRENT_LLM=3         # 3 LLMs = 9-12GB RAM = HANG!
OLLAMA_TIMEOUT=50
OLLAMA_MAX_ARTICLES=10

# NEW (16GB RAM optimized)
MAX_CONCURRENT_SCRAPES=3     # Reduced to 3 parallel scrapes
MAX_CONCURRENT_LLM=1         # CRITICAL: Only 1 LLM at a time!
OLLAMA_TIMEOUT=60            # Increased timeout for safety
OLLAMA_MAX_ARTICLES=5        # Process fewer articles
OLLAMA_TOTAL_TIMEOUT=480     # 8 minutes total
```

**Why This Helps**:
- **1 LLM at a time** = ~4GB RAM usage (safe for 16GB system)
- **3 LLMs at a time** = ~12GB RAM = System hangs! ❌

### **2. Ollama Service Settings** (`ollama_service.py`)

**Changed**:
```python
# OLD (Server settings)
"num_ctx": 1536,      # Large context = more RAM
"num_thread": 10,     # Too many threads for 4-core CPU
"num_batch": default  # Default batch size

# NEW (16GB RAM optimized)
"num_ctx": 1024,      # Smaller context = less RAM
"num_thread": 4,      # Match CPU cores (4 cores = 8 threads)
"num_batch": 128      # Smaller batches = less memory
```

---

## 🚀 How to Apply (Step-by-Step)

### **Step 1: Set Ollama Environment Variables** (MOST IMPORTANT!)

Run these commands in **PowerShell as Administrator**:

```powershell
# Set environment variables for Ollama
[System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_PARALLEL', '1', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_MAX_LOADED_MODELS', '1', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_THREADS', '4', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_CTX', '1024', 'Machine')

# Verify settings
[System.Environment]::GetEnvironmentVariable('OLLAMA_NUM_PARALLEL', 'Machine')
```

### **Step 2: Restart Ollama Service**

```powershell
# Stop Ollama
taskkill /F /IM ollama.exe

# Wait 5 seconds
Start-Sleep -Seconds 5

# Start Ollama
Start-Process "C:\Users\anupamb\AppData\Local\Programs\Ollama\ollama.exe" -ArgumentList "serve"
```

Or restart via system tray:
1. Right-click Ollama icon in system tray
2. Click "Quit Ollama"
3. Start Ollama again from Start menu

### **Step 3: Restart Backend Server**

```powershell
# Stop current backend (Ctrl+C in terminal)

# Start with new settings
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

---

## 📊 Performance Comparison

| Configuration | LLMs Running | RAM Usage | Status |
|--------------|--------------|-----------|--------|
| **OLD (Server)** | 3 parallel | ~12GB | ❌ Hangs! |
| **NEW (16GB)** | 1 sequential | ~4GB | ✅ Stable! |

### Expected Processing Time:

**OLD (Parallel - Hangs)**:
- 5 articles ÷ 3 parallel = ~2 minutes (if it worked)
- But system hangs! ❌

**NEW (Sequential - Stable)**:
- 5 articles × 1 at a time = ~5-6 minutes
- System remains responsive ✅
- Real-time streaming still works!

---

## 🧪 Test After Applying

### **1. Check Ollama Settings**

```powershell
# Verify environment variables
[System.Environment]::GetEnvironmentVariable('OLLAMA_NUM_PARALLEL', 'Machine')
# Should show: 1

[System.Environment]::GetEnvironmentVariable('OLLAMA_MAX_LOADED_MODELS', 'Machine')
# Should show: 1

[System.Environment]::GetEnvironmentVariable('OLLAMA_NUM_THREADS', 'Machine')
# Should show: 4
```

### **2. Test Search**

1. Open: http://localhost:5173
2. Search: "bombing in Kabul"
3. Watch progress bar
4. **Expected**:
   - ✅ Progress bar updates smoothly
   - ✅ System remains responsive
   - ✅ Events appear one-by-one (~60s each)
   - ✅ No hanging!

### **3. Monitor Resource Usage**

**While searching, check Task Manager**:
- CPU: Should be ~50-80% (not 100%)
- RAM: Should be ~8-10GB (not maxed out)
- Ollama process: ~4GB RAM

---

## ⚠️ Important Notes

### **Why Sequential Processing?**

Your system has:
- **16GB RAM** (15.8GB usable)
- **4 CPU cores**

Running **3 LLMs in parallel**:
- Each LLM uses ~4GB RAM
- 3 × 4GB = **12GB just for LLMs**
- Plus Windows, browser, backend = **16GB+ total**
- Result: **System swaps to disk → Hangs!** ❌

Running **1 LLM at a time**:
- 1 × 4GB = **4GB for LLM**
- Plus system overhead = **~8GB total**
- Result: **8GB free RAM → Smooth!** ✅

### **Trade-off**

| Aspect | Before | After |
|--------|--------|-------|
| Speed | 2-3 min (if it worked) | 5-6 min |
| Stability | Hangs ❌ | Stable ✅ |
| Real-time | Yes | Yes ✅ |
| User Experience | Frozen system | Responsive system ✅ |

**5-6 minutes with real-time updates is better than a frozen system!**

---

## 🔧 Advanced: Reduce Articles Processed

If 5 articles is still too slow, edit `backend/.env`:

```properties
OLLAMA_MAX_ARTICLES=3  # Process only 3 articles (faster)
```

**Result**: ~3 minutes total, 3 events

---

## 🎯 Alternative: Use Smaller Model

If qwen2.5:3b is still too heavy, try a smaller model:

```powershell
# Download smaller model
ollama pull qwen2.5:1.5b

# Update backend/.env
OLLAMA_MODEL=qwen2.5:1.5b
```

**qwen2.5:1.5b**:
- Size: ~1GB (vs 2GB for 3b)
- RAM: ~2GB (vs 4GB for 3b)
- Speed: 2x faster
- Quality: Slightly lower but still good

---

## ✅ Summary of Changes

### **Files Modified**:

1. **`backend/.env`**:
   - `MAX_CONCURRENT_LLM=1` (was 3)
   - `MAX_CONCURRENT_SCRAPES=3` (was 10)
   - `OLLAMA_MAX_ARTICLES=5` (was 10)
   - `OLLAMA_TIMEOUT=60` (was 50)

2. **`backend/app/services/ollama_service.py`**:
   - `num_ctx=1024` (was 1536)
   - `num_thread=4` (was 10)
   - `num_batch=128` (new)

3. **Ollama Environment Variables** (to set):
   - `OLLAMA_NUM_PARALLEL=1`
   - `OLLAMA_MAX_LOADED_MODELS=1`
   - `OLLAMA_NUM_THREADS=4`
   - `OLLAMA_NUM_CTX=1024`

---

## 🚀 Quick Start Checklist

- [ ] Set Ollama environment variables (PowerShell as Admin)
- [ ] Restart Ollama service
- [ ] Restart backend server
- [ ] Test search with "bombing in Kabul"
- [ ] Verify system stays responsive
- [ ] Monitor Task Manager (RAM usage)

---

## 📞 If Still Hanging

1. **Check Ollama logs**:
   ```powershell
   Get-Content "$env:USERPROFILE\.ollama\logs\server.log" -Tail 50
   ```

2. **Reduce to 3 articles**:
   ```properties
   # backend/.env
   OLLAMA_MAX_ARTICLES=3
   ```

3. **Use smaller model**:
   ```powershell
   ollama pull qwen2.5:1.5b
   ```

4. **Check memory**:
   - Close Chrome/Edge
   - Close other applications
   - Free up RAM

---

## ✅ Expected Outcome

After applying these settings:
- ✅ System remains responsive during search
- ✅ Progress bar updates smoothly
- ✅ Events stream in real-time (one every ~60s)
- ✅ No hanging or freezing
- ✅ CPU ~50-80%, RAM ~8-10GB
- ⏱️ Total time: 5-6 minutes for 5 events

**Better to wait 5 minutes with a responsive system than have a frozen computer!** 🎯
