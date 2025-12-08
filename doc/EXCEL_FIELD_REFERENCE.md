# Excel Export Field Reference

## Quick Reference: All 18 Exported Fields

### 📋 Column Layout

```
┌─────┬──────────────────────────────┬──────────────────────────────────────┐
│ Col │ Field Name                   │ Description & Example                │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  A  │ Event Title                  │ Article headline                     │
│     │                              │ "Bomb blast kills 5 in Kabul"        │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  B  │ Summary                      │ 1-2 sentence summary                 │
│     │                              │ "A suicide bombing near Kabul..."    │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  C  │ Event Type                   │ Category: BOMBING, ATTACK, PROTEST   │
│     │                              │ "BOMBING"                            │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  D  │ Perpetrator                  │ Who carried out the event            │
│     │                              │ "Taliban", "Unknown", or empty       │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  E  │ Location (Full Text)         │ Complete location string             │
│     │                              │ "Kabul, Kabul Province, Afghanistan" │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  F  │ City                         │ Parsed city name                     │
│     │                              │ "Kabul"                              │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  G  │ Region/State                 │ Parsed region/state/province         │
│     │                              │ "Kabul Province"                     │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  H  │ Country                      │ Parsed country                       │
│     │                              │ "Afghanistan"                        │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  I  │ Event Date                   │ When event occurred (YYYY-MM-DD)     │
│     │                              │ "2023-01-02"                         │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  J  │ Event Time                   │ Time of day if available             │
│     │                              │ "09:30", "morning", or empty         │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  K  │ Individuals Involved         │ Comma-separated list of people       │
│     │                              │ "John Doe, Jane Smith"               │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  L  │ Organizations Involved       │ Comma-separated list of orgs         │
│     │                              │ "Taliban, UN, Red Cross"             │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  M  │ Casualties (Killed)          │ Number of people killed              │
│     │                              │ "5" or empty if not mentioned        │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  N  │ Casualties (Injured)         │ Number of people injured             │
│     │                              │ "12" or empty if not mentioned       │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  O  │ Source Name                  │ News source                          │
│     │                              │ "BBC News", "Reuters", "CNN"         │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  P  │ Source URL                   │ Article link (hyperlinked)           │
│     │                              │ "https://bbc.com/news/..."           │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  Q  │ Article Publication Date     │ When article was published           │
│     │                              │ "2023-01-03"                         │
├─────┼──────────────────────────────┼──────────────────────────────────────┤
│  R  │ Extraction Confidence        │ Quality score (0-100%)               │
│     │                              │ "85%"                                │
└─────┴──────────────────────────────┴──────────────────────────────────────┘
```

---

## 🎯 Field Mapping

### **From LLM Response:**

```json
{
  "event_type": "bombing",                    → Column C
  "summary": "Brief description...",          → Column B
  "perpetrator": "Taliban",                   → Column D
  "location": {
    "city": "Kabul",                          → Column F
    "region": "Kabul Province",               → Column G
    "country": "Afghanistan"                  → Column H
  },
  "event_date": "2023-01-02",                 → Column I
  "event_time": "09:30",                      → Column J
  "individuals": ["Person A", "Person B"],    → Column K
  "organizations": ["Taliban", "UN"],         → Column L
  "casualties": {
    "killed": 5,                              → Column M
    "injured": 12                             → Column N
  },
  "confidence": 0.85                          → Column R
}
```

### **From Article Metadata:**

```python
article.title                → Column A (Event Title)
article.source_name          → Column O (Source Name)
article.url                  → Column P (Source URL)
article.published_date       → Column Q (Article Publication Date)
```

### **From Combined Location:**

```python
str(location)  → Column E (Location Full Text)
# Combines: "Kabul, Kabul Province, Afghanistan"
```

---

## 📊 Data Types

| Column | Type | Format | Nullable |
|--------|------|--------|----------|
| A | String | Text | No |
| B | String | Text | No |
| C | Enum | UPPERCASE_WORDS | No |
| D | String | Text | Yes |
| E | String | "City, Region, Country" | Yes |
| F | String | Text | Yes |
| G | String | Text | Yes |
| H | String | Text | Yes |
| I | Date | YYYY-MM-DD | Yes |
| J | String | HH:MM or text | Yes |
| K | String | Comma-separated | Yes |
| L | String | Comma-separated | Yes |
| M | Integer | Number | Yes |
| N | Integer | Number | Yes |
| O | String | Text | Yes |
| P | URL | Hyperlinked text | Yes |
| Q | Date | YYYY-MM-DD | Yes |
| R | Percentage | XX% | No |

---

## 🔍 Field Validation Rules

### **Event Title (A)**
- ✅ Must be non-empty
- ✅ Taken from article headline
- ✅ Max recommended: 100 characters

### **Summary (B)**
- ✅ 1-2 sentences
- ✅ Extracted by LLM
- ✅ Max recommended: 300 characters

### **Event Type (C)**
- ✅ Must be valid EventType enum
- ✅ Auto-validated with fuzzy matching
- ✅ Defaults to "OTHER" if unknown

### **Perpetrator (D)**
- ⚠️ Optional (attacks/bombings only)
- ✅ Can be "Unknown", org name, or null
- ✅ Separate from "Individuals Involved"

### **Location Fields (E, F, G, H)**
- ✅ Full text combines all components
- ✅ Components can be individually null
- ✅ Extracted by LLM from article text

### **Event Date (I)**
- ✅ Format: YYYY-MM-DD
- ✅ Fallback: Article publication date
- ✅ Parsed with multiple format attempts

### **Event Time (J)**
- ⚠️ Optional
- ✅ Formats: "HH:MM", "morning", "evening", "night"
- ✅ Extracted if mentioned in article

### **Individuals/Organizations (K, L)**
- ✅ Comma-separated lists
- ✅ Combined from LLM + NLP entities
- ✅ Deduplicated

### **Casualties (M, N)**
- ⚠️ Optional (if numbers mentioned)
- ✅ Integers only
- ✅ Separate killed vs injured counts

### **Source Name (O)**
- ✅ Auto-detected from URL
- ✅ 15+ major sources recognized
- ✅ Fallback: Domain name

### **Source URL (P)**
- ✅ Must be valid URL
- ✅ Hyperlinked in Excel
- ✅ Blue, underlined formatting

### **Article Publication Date (Q)**
- ✅ Format: YYYY-MM-DD
- ✅ Fallback: Event date if missing
- ✅ From article metadata

### **Extraction Confidence (R)**
- ✅ Range: 0% - 100%
- ✅ LLM self-assessment
- ✅ Default: 75% if not provided

---

## 🎨 Excel Styling

### **Header Row**
- Background: Dark Blue (#366092)
- Font: White, Bold, 11pt
- Alignment: Center

### **Data Rows**
- Zebra striping: Alternating light gray (#F2F2F2)
- Font: Regular, 10pt
- Alignment: Top-left, wrap text

### **Special Formatting**
- **Event Title (A)**: Bold
- **Source URL (P)**: Blue (#0563C1), underlined, hyperlinked

### **Column Widths**
- Event Title: 40
- Summary: 60
- Location (Full): 35
- Others: Auto-adjusted (10-30)

---

## 🔄 Processing Pipeline

```
1. Article Scraped
   ↓
2. Extract metadata (title, URL, date, source)
   ↓
3. NLP entity extraction (spaCy)
   ↓
4. LLM event extraction (Ollama)
   ↓
5. Parse LLM JSON response
   ↓
6. Enrich with entities
   ↓
7. Apply fallbacks for missing data
   ↓
8. Create EventData object (18 fields)
   ↓
9. Format for Excel
   ↓
10. Apply styling
   ↓
11. Export .xlsx file
```

---

## ✅ Quality Checklist

Before accepting extraction results:

- [ ] **All 18 columns present** in Excel export
- [ ] **Event Title** populated for all rows
- [ ] **Event Type** is valid enum (not "OTHER" for all)
- [ ] **Location** has at least one component (city, region, or country)
- [ ] **Event Date** in correct format (YYYY-MM-DD)
- [ ] **Source Name** identified (not just URL)
- [ ] **Confidence** between 0-100%
- [ ] **Casualties** extracted if mentioned in article
- [ ] **Hyperlinks** working on Source URL column
- [ ] **No critical fields** completely empty across all events

---

## 📈 Expected Completion Rates

| Field | Typical Fill Rate |
|-------|------------------|
| Event Title | 100% |
| Summary | 100% |
| Event Type | 100% |
| Perpetrator | 40-60% (attack events only) |
| Location (Full) | 95% |
| City | 80-90% |
| Region/State | 60-70% |
| Country | 90-95% |
| Event Date | 95% |
| Event Time | 30-50% |
| Individuals Involved | 70-85% |
| Organizations Involved | 60-80% |
| Casualties (Killed) | 40-60% (attack events) |
| Casualties (Injured) | 40-60% (attack events) |
| Source Name | 100% |
| Source URL | 100% |
| Article Publication Date | 95% |
| Extraction Confidence | 100% |

---

**Reference Version**: 2.0  
**Last Updated**: December 6, 2025  
**For**: Production Event Extraction System
