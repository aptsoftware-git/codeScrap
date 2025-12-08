# Production Testing Checklist

## 🧪 Pre-Deployment Testing Guide

**Version**: 2.0  
**Date**: December 6, 2025  
**Status**: Ready for Testing

---

## ✅ System Status Verification

### **1. Backend Server**

- [x] Virtual environment activated (`venv`)
- [x] Server running on http://127.0.0.1:8000
- [x] Uvicorn auto-reload enabled
- [x] All modules loaded successfully:
  - [x] ConfigManager initialized
  - [x] spaCy model loaded (en_core_web_sm)
  - [x] OllamaClient initialized
  - [x] EventExtractor initialized
  - [x] ExcelExporter initialized
  - [x] 7 sources loaded (1 enabled: DuckDuckGo)

### **2. Frontend** (If applicable)

- [ ] Frontend server running
- [ ] Can access search interface
- [ ] API connection working

---

## 🎯 Test Cases

### **Test Case 1: Bombing Event (Comprehensive)**

**Objective**: Verify all 18 fields are extracted correctly

**Steps**:
1. Open frontend or use API: `POST /api/v1/search`
2. Enter query: `"bombing in Kabul in January 2023"`
3. Wait for processing (~60 seconds)
4. Download Excel export

**Expected Results**:

| Field | Expected Value | ✓ |
|-------|---------------|---|
| Event Title | Should contain "Kabul", "bombing", "airport" or similar | [ ] |
| Summary | 1-2 sentences describing the bombing | [ ] |
| Event Type | BOMBING, EXPLOSION, or ATTACK | [ ] |
| Perpetrator | "Taliban", "Islamic State", "ISIS-K", or "Unknown" | [ ] |
| Location (Full) | "Kabul, Kabul Province, Afghanistan" or similar | [ ] |
| City | "Kabul" | [ ] |
| Region/State | "Kabul Province" or similar | [ ] |
| Country | "Afghanistan" | [ ] |
| Event Date | 2023-01-XX (January 2023) | [ ] |
| Event Time | Time if mentioned, or empty | [ ] |
| Individuals Involved | Names if mentioned (may be empty) | [ ] |
| Organizations Involved | "Taliban", "UN", "Red Cross", etc. | [ ] |
| Casualties (Killed) | Number (e.g., 5, 10) or empty | [ ] |
| Casualties (Injured) | Number (e.g., 12, 20) or empty | [ ] |
| Source Name | "BBC News", "Reuters", "Wikipedia", "CNN", etc. | [ ] |
| Source URL | Full URL, hyperlinked | [ ] |
| Article Publication Date | 2023-01-XX or 2023-01-XX | [ ] |
| Extraction Confidence | 70-95% typical | [ ] |

**Quality Checks**:
- [ ] At least 3-5 events extracted
- [ ] Average confidence > 70%
- [ ] All 18 columns present
- [ ] No completely empty critical fields (Title, Summary, Event Type)
- [ ] Source URLs are clickable hyperlinks
- [ ] Dates in YYYY-MM-DD format

---

### **Test Case 2: Protest Event**

**Objective**: Verify non-violence event extraction

**Steps**:
1. Query: `"Kashmir protest 2024"`
2. Download Excel

**Expected Results**:
- [ ] Event Type: PROTEST or DEMONSTRATION
- [ ] Perpetrator: Empty or null (not applicable)
- [ ] Location: Kashmir region identified
- [ ] Casualties: Empty (peaceful protest)
- [ ] Organizations: Protest groups, political parties
- [ ] Confidence: >70%

---

### **Test Case 3: Multiple Sources**

**Objective**: Verify source diversity and name extraction

**Steps**:
1. Query: `"Afghanistan terrorism January 2023"`
2. Check 5 extracted events

**Expected Results**:
- [ ] At least 3 different source names
- [ ] Source names correctly identified:
  - [ ] BBC News (from bbc.com)
  - [ ] Reuters (from reuters.com)
  - [ ] CNN (from cnn.com)
  - [ ] Wikipedia (from wikipedia.org)
  - [ ] CBS News (from cbsnews.com)
- [ ] All Source URLs hyperlinked
- [ ] Each event from different article

---

### **Test Case 4: Date Parsing**

**Objective**: Verify date extraction and fallback logic

**Steps**:
1. Query: `"Kabul attack 2023"`
2. Check Event Date column

**Expected Results**:
- [ ] Event dates in YYYY-MM-DD format
- [ ] Dates match article content
- [ ] If Event Date missing, Article Publication Date used
- [ ] No future dates (unless article is predictive)

---

### **Test Case 5: Location Parsing**

**Objective**: Verify location component separation

**Steps**:
1. Query: `"bombing in Kabul"`
2. Check location columns

**Expected Results**:
- [ ] Location (Full): Combined string
- [ ] City: Parsed separately
- [ ] Region/State: Parsed separately
- [ ] Country: Parsed separately
- [ ] All components consistent

**Example**:
```
Location (Full): Kabul, Kabul Province, Afghanistan
City: Kabul
Region/State: Kabul Province
Country: Afghanistan
```

---

### **Test Case 6: Casualty Extraction**

**Objective**: Verify casualty counting

**Steps**:
1. Query: `"Kabul bombing casualties"`
2. Check casualty columns

**Expected Results**:
- [ ] Casualties (Killed): Integer or empty
- [ ] Casualties (Injured): Integer or empty
- [ ] Numbers match article (if mentioned)
- [ ] Empty if not mentioned (not "0")

---

### **Test Case 7: Perpetrator Identification**

**Objective**: Verify perpetrator extraction for attacks

**Steps**:
1. Query: `"Taliban attack 2023"`
2. Check Perpetrator column

**Expected Results**:
- [ ] Attack events: Perpetrator identified
- [ ] "Taliban", "ISIS-K", "Islamic State", or "Unknown"
- [ ] Non-attack events: Empty or null
- [ ] No false perpetrators for accidents/disasters

---

### **Test Case 8: Excel Export Quality**

**Objective**: Verify Excel formatting and usability

**Steps**:
1. Download Excel file from any search
2. Open in Microsoft Excel or LibreOffice

**Expected Results**:
- [ ] **Header Row**: Dark blue background, white text, bold
- [ ] **Zebra Striping**: Alternating gray rows
- [ ] **Frozen Panes**: Header row and Event Title column frozen
- [ ] **Column Widths**: Readable without manual adjustment
- [ ] **Hyperlinks**: Source URL clickable and blue
- [ ] **Summary Sheet**: Present with statistics
- [ ] **File Size**: Reasonable (<5 MB for 50 events)

---

### **Test Case 9: Confidence Scoring**

**Objective**: Verify LLM confidence assessment

**Steps**:
1. Query: `"bombing in Kabul in January 2023"`
2. Check Extraction Confidence column

**Expected Ranges**:
- [ ] **90-100%**: Very clear events (1-2 expected)
- [ ] **75-89%**: Good quality (3-4 expected)
- [ ] **60-74%**: Fair quality (0-1 expected)
- [ ] **<60%**: Poor quality (should be rare)

**Red Flags**:
- [ ] All events <70% → Review article quality
- [ ] All events >95% → May be too optimistic

---

### **Test Case 10: Performance**

**Objective**: Verify acceptable processing time

**Steps**:
1. Query: `"bombing in Kabul"`
2. Measure time from submit to download

**Expected Results**:
- [ ] Total time: 60-90 seconds (5 articles)
- [ ] No timeout errors
- [ ] Responsive UI during processing
- [ ] Progress indicators working (if frontend)

**Breakdown**:
- [ ] Search: ~2s
- [ ] Scrape 5 articles: ~10s
- [ ] LLM extraction: ~50s
- [ ] Excel export: ~1s

---

## 📊 Quality Metrics

After testing, calculate:

### **Field Completeness**

Count how many events have each field populated:

```
Event Title:               ___ / 5 (should be 5/5)
Summary:                   ___ / 5 (should be 5/5)
Event Type:                ___ / 5 (should be 5/5)
Perpetrator:               ___ / 5 (2-4/5 for attacks)
Location (Full):           ___ / 5 (4-5/5)
City:                      ___ / 5 (4-5/5)
Region/State:              ___ / 5 (3-4/5)
Country:                   ___ / 5 (4-5/5)
Event Date:                ___ / 5 (4-5/5)
Event Time:                ___ / 5 (1-3/5)
Individuals Involved:      ___ / 5 (3-4/5)
Organizations Involved:    ___ / 5 (3-4/5)
Casualties (Killed):       ___ / 5 (2-3/5 for attacks)
Casualties (Injured):      ___ / 5 (2-3/5 for attacks)
Source Name:               ___ / 5 (should be 5/5)
Source URL:                ___ / 5 (should be 5/5)
Article Publication Date:  ___ / 5 (4-5/5)
Extraction Confidence:     ___ / 5 (should be 5/5)
```

### **Accuracy Checks**

Manually verify 2-3 events:

| Event # | Title Accurate | Location Correct | Date Correct | Casualties Correct | Overall |
|---------|---------------|------------------|--------------|-------------------|---------|
| 1 | [ ] | [ ] | [ ] | [ ] | [ ] |
| 2 | [ ] | [ ] | [ ] | [ ] | [ ] |
| 3 | [ ] | [ ] | [ ] | [ ] | [ ] |

---

## 🚨 Known Limitations

### **Expected Behavior** (Not Bugs):

1. **Perpetrator Empty for Non-Attacks**
   - Normal for protests, conferences, elections
   - Only populated for attacks, bombings, violence

2. **Event Time Often Empty**
   - Many articles don't mention specific time
   - 30-50% fill rate is normal

3. **Region/State Lower Fill Rate**
   - Some locations don't have regions in articles
   - 60-70% is acceptable

4. **Casualties Only for Violence**
   - Empty for protests, conferences, etc.
   - Only populated when numbers mentioned

5. **Confidence Variation**
   - Depends on article clarity
   - 70-90% is typical range
   - <70% may need manual review

---

## ❌ Failure Scenarios to Test

### **Error Handling**:

1. **No Articles Found**
   - [ ] Query: `"xyzabc123nonsense"`
   - [ ] Expected: Error message, no crash

2. **Network Issues**
   - [ ] Disconnect internet mid-search
   - [ ] Expected: Graceful error, retry or fail cleanly

3. **Invalid Query**
   - [ ] Query: Empty string
   - [ ] Expected: Validation error

4. **LLM Timeout**
   - [ ] (Simulate by overloading Ollama)
   - [ ] Expected: Timeout error, partial results

---

## ✅ Sign-Off Criteria

System is **PRODUCTION READY** when:

- [ ] All 10 test cases pass
- [ ] Field completeness >85% average
- [ ] Accuracy checks >90% correct
- [ ] No critical bugs found
- [ ] Performance <2 minutes per search
- [ ] Excel exports open correctly
- [ ] Documentation complete
- [ ] Error handling graceful

---

## 📝 Testing Notes

**Tester**: _________________  
**Date**: _________________  
**Version Tested**: 2.0

### **Issues Found**:

1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

### **Recommendations**:

1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

### **Overall Assessment**:

- [ ] ✅ **PASS** - Ready for production
- [ ] ⚠️ **CONDITIONAL** - Minor fixes needed
- [ ] ❌ **FAIL** - Major issues, needs rework

---

## 🚀 Post-Testing Actions

Once testing passes:

1. [ ] Update `CHANGELOG.md` with v2.0 changes
2. [ ] Create production deployment plan
3. [ ] Set up monitoring/logging
4. [ ] Train users on new 18-field export
5. [ ] Plan data migration (if existing system)
6. [ ] Schedule production rollout

---

**Testing Guide Version**: 1.0  
**Last Updated**: December 6, 2025  
**Next Review**: After first production test
