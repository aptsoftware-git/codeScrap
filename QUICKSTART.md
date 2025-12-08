# Quick Start Guide - Production v2.0

## ✅ System Ready!

**Backend Server**: ✅ Running on http://127.0.0.1:8000  
**Virtual Environment**: ✅ Activated  
**All Services**: ✅ Loaded Successfully

---

## 🚀 How to Test Right Now

### **Option 1: Using API (Recommended for testing)**

1. **Open your browser or Postman**
2. **Send POST request**:
   ```
   URL: http://127.0.0.1:8000/api/v1/search
   Method: POST
   Headers: Content-Type: application/json
   Body:
   {
     "phrase": "bombing in Kabul in January 2023",
     "max_results": 5
   }
   ```

3. **Wait for response** (~60 seconds)

4. **Extract session_id** from response

5. **Download Excel**:
   ```
   GET: http://127.0.0.1:8000/api/v1/export/{session_id}
   ```

---

### **Option 2: Using Frontend (If available)**

1. Start frontend (if not running):
   ```powershell
   cd C:\Anu\APT\apt\defender\scraping\code\frontend
   npm run dev
   ```

2. Open browser: http://localhost:3000 (or frontend port)

3. Enter search query: `"bombing in Kabul in January 2023"`

4. Click "Search"

5. Wait for results (~60 seconds)

6. Click "Export to Excel"

---

## 📊 What You'll See

### **Backend Logs (Watch the terminal)**:

```
✅ DuckDuckGo search complete
✅ Found 10 article links
✅ Scraping 5 articles...
✅ Processing article 1/5: [Title]...
✅ Extracted event: BOMBING (confidence: 0.85)
✅ Processing article 2/5: [Title]...
...
✅ Successfully extracted 5/5 events
✅ Creating Excel export...
✅ Excel export ready for download
```

### **Excel File Columns (All 18)**:

```
A: Event Title
B: Summary
C: Event Type
D: Perpetrator
E: Location (Full Text)
F: City
G: Region/State
H: Country
I: Event Date
J: Event Time
K: Individuals Involved
L: Organizations Involved
M: Casualties (Killed)
N: Casualties (Injured)
O: Source Name
P: Source URL (Hyperlinked)
Q: Article Publication Date
R: Extraction Confidence
```

---

## ✅ Verification Checklist

Open the Excel file and verify:

- [ ] **18 columns** present (A-R)
- [ ] **Header row** is dark blue with white text
- [ ] **5 data rows** (one per article)
- [ ] **Event Title** column has article headlines
- [ ] **Event Type** shows BOMBING, EXPLOSION, or ATTACK
- [ ] **Perpetrator** shows Taliban, ISIS-K, or Unknown (or empty)
- [ ] **City** column shows "Kabul"
- [ ] **Country** column shows "Afghanistan"
- [ ] **Event Date** in YYYY-MM-DD format
- [ ] **Source Name** shows "BBC News", "Reuters", "Wikipedia", etc.
- [ ] **Source URL** is blue and clickable
- [ ] **Confidence** shows percentages (70-95%)
- [ ] **Summary Sheet** tab exists

---

## 🎯 Sample Query & Expected Results

### **Query 1: Bombing Events**
```
"bombing in Kabul in January 2023"
```

**Expected**:
- 5 articles about Kabul bombings
- Event Type: BOMBING, EXPLOSION, ATTACK
- Perpetrator: Taliban, Islamic State, or Unknown
- Casualties: Numbers extracted
- Confidence: 75-90%

---

### **Query 2: Protest Events**
```
"Kashmir protest 2024"
```

**Expected**:
- 5 articles about Kashmir protests
- Event Type: PROTEST, DEMONSTRATION
- Perpetrator: Empty (not applicable)
- Casualties: Empty (peaceful)
- Confidence: 70-85%

---

### **Query 3: Diverse Sources**
```
"Afghanistan terrorism January 2023"
```

**Expected**:
- 5 articles from different sources
- Source Names: BBC, Reuters, CNN, Wikipedia, etc.
- Event Types: Mix of BOMBING, ATTACK, TERRORIST_ACTIVITY
- Confidence: 70-90%

---

## 🔍 How to Read the Results

### **High Quality Event (Confidence >85%)**:
```
Title: "Kabul Airport Bombing Kills 5, Wounds 12"
Summary: "A suicide bombing near Kabul airport killed 5 people..."
Event Type: BOMBING
Perpetrator: Islamic State
Location: Kabul, Kabul Province, Afghanistan
City: Kabul
Country: Afghanistan
Event Date: 2023-01-02
Casualties (Killed): 5
Casualties (Injured): 12
Source Name: BBC News
Confidence: 88%
```

### **Moderate Quality Event (Confidence 70-85%)**:
```
Title: "Explosion Reported in Kabul"
Summary: "An explosion occurred near a checkpoint..."
Event Type: EXPLOSION
Perpetrator: Unknown
Location: Kabul, Afghanistan
City: Kabul
Country: Afghanistan
Event Date: 2023-01-01
Casualties (Killed): [empty]
Casualties (Injured): [empty]
Source Name: Reuters
Confidence: 72%
```

---

## ⚠️ What's Normal (Not Bugs)

### **Expected Empty Fields**:

1. **Perpetrator**: Empty for non-attack events (protests, conferences)
2. **Event Time**: Often empty (not mentioned in articles)
3. **Region/State**: Sometimes empty (not always specified)
4. **Casualties**: Empty if not mentioned in article
5. **Individuals Involved**: May be empty if no names mentioned

### **Expected Variations**:

1. **Confidence 60-95%**: Normal range, depends on article clarity
2. **Different Event Types**: Same event may be BOMBING vs ATTACK vs EXPLOSION
3. **Source Names**: Auto-detected, may be domain name if not recognized
4. **Date Fallbacks**: Article pub date used if event date not found

---

## 🐛 Troubleshooting

### **Problem: No articles found**

**Causes**:
- DuckDuckGo has no results for query
- Link extraction failing

**Solutions**:
- Check logs: `backend/logs/app.log`
- Try different query
- Verify DuckDuckGo is not blocking (rare)

---

### **Problem: Low confidence scores (<70%)**

**Causes**:
- Article is unclear or ambiguous
- Multiple events in one article
- Missing key information

**Solutions**:
- Normal for some articles
- Review article quality manually
- Try more specific queries

---

### **Problem: Excel file won't open**

**Causes**:
- File corrupted
- Excel/LibreOffice not installed

**Solutions**:
- Download again
- Try LibreOffice Calc
- Check file size (should be >10 KB)

---

### **Problem: Missing perpetrator data**

**Causes**:
- Not an attack/violence event
- Perpetrator not mentioned
- LLM unable to identify

**Solutions**:
- Normal for non-attacks
- Check article manually
- Use "Unknown" as indicator

---

## 📞 Need Help?

### **Check These First**:

1. **Server Logs**: 
   ```
   C:\Anu\APT\apt\defender\scraping\code\backend\logs\app.log
   ```

2. **Terminal Output**: 
   Watch the server terminal for errors

3. **Documentation**:
   - `doc/PRODUCTION_EXTRACTION_GUIDE.md` - Complete guide
   - `doc/EXCEL_FIELD_REFERENCE.md` - Field reference
   - `doc/TESTING_CHECKLIST.md` - Testing guide
   - `doc/IMPLEMENTATION_SUMMARY.md` - Implementation details

---

## 🎉 Success Indicators

You know it's working when:

- ✅ Search completes in ~60 seconds
- ✅ Excel file downloads successfully
- ✅ 18 columns present in Excel
- ✅ 5 events extracted
- ✅ Event titles are article headlines
- ✅ Event types make sense (BOMBING, ATTACK, etc.)
- ✅ Locations parsed correctly
- ✅ Source names identified (BBC, Reuters, etc.)
- ✅ Confidence scores >70%
- ✅ No crashes or errors

---

## 📈 Next Steps

### **After First Successful Test**:

1. [ ] Try 3-5 different queries
2. [ ] Verify field accuracy manually
3. [ ] Check confidence score patterns
4. [ ] Review perpetrator identification
5. [ ] Test with different event types (protests, conferences)
6. [ ] Share Excel export with team for feedback
7. [ ] Plan production deployment

---

## 🚀 Production Deployment Prep

When ready for production:

1. **Set log level** to INFO or WARNING:
   ```python
   # backend/app/config.py
   log_level: str = "INFO"  # Change from DEBUG
   ```

2. **Review rate limits**:
   ```yaml
   # config/sources.yaml
   rate_limit: 2.0  # Increase if needed for production load
   ```

3. **Set up monitoring**:
   - Track confidence scores
   - Monitor field completeness
   - Log extraction failures

4. **Create backup plan**:
   - Export sample data
   - Document configuration
   - Plan rollback strategy

---

**Version**: 2.0  
**Status**: ✅ **READY FOR TESTING**  
**Server**: ✅ **RUNNING**  
**Next**: **RUN YOUR FIRST TEST QUERY** 🎯

---

**Quick Test Command** (PowerShell/cmd):
```powershell
# Test API endpoint
curl -X POST http://127.0.0.1:8000/api/v1/search `
  -H "Content-Type: application/json" `
  -d '{\"phrase\": \"bombing in Kabul in January 2023\", \"max_results\": 5}'
```

**Expected Response**: JSON with `session_id` and extracted events!

---

**🎊 YOU'RE ALL SET! START TESTING! 🎊**
