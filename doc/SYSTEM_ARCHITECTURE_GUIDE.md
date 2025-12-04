# Event Scraper System Architecture Guide

**Date**: December 3, 2025  
**Version**: 1.0  
**Purpose**: Complete guide to understand how the system works

---

## Table of Contents
1. [Web Scraper Architecture](#1-web-scraper-architecture)
2. [spaCy NLP Processing](#2-spacy-nlp-processing)
3. [LLM Model Role](#3-llm-model-role)
4. [Complete Workflow](#4-complete-workflow)

---

## 1. Web Scraper Architecture

### Overview
The web scraper is a **configurable, multi-source scraping system** that extracts news articles from various websites based on user search queries.

### How It Works

#### Step 1: Configuration Loading
```yaml
# config/sources.yaml
sources:
  - name: "SATP"
    base_url: "https://www.satp.org"
    enabled: true
    search_url_template: "https://www.satp.org/terrorist-activity/southasia?search={query}"
    rate_limit: 3.0
    selectors:
      article_links: "a[href*='terrorist-activity']"
      title: "h1, h2.article-title"
      content: "article, div.content, p"
      date: "time, span.date"
```

**What happens:**
1. System reads `sources.yaml` on startup
2. Loads all sources where `enabled: true`
3. Creates a scraper instance for each enabled source

#### Step 2: Search Process

```
User Search: "Kashmir terrorism"
       ↓
1. Query Processing
   - Sanitize input: "Kashmir terrorism"
   - URL encode: "Kashmir%20terrorism"
   
       ↓
2. URL Generation (for each enabled source)
   - Template: "https://www.satp.org/...?search={query}"
   - Final URL: "https://www.satp.org/...?search=Kashmir%20terrorism"
   
       ↓
3. HTTP Request
   - Send GET request with headers from config
   - Wait for rate_limit seconds before next request
   - Handle timeouts, retries
   
       ↓
4. HTML Parsing
   - Receive HTML response
   - Parse with BeautifulSoup4
   
       ↓
5. Article Discovery
   - Use selector: article_links: "a[href*='terrorist-activity']"
   - Find all matching <a> tags
   - Extract href attributes
   - Example found: [
       "https://www.satp.org/terrorist-activity/india-kashmir-2025",
       "https://www.satp.org/terrorist-activity/pakistan-2025",
       ...
     ]
   
       ↓
6. Article Scraping (for each article link)
   - Visit article URL
   - Extract content using selectors:
     * title: "h1, h2.article-title"
     * content: "article, div.content, p"
     * date: "time, span.date"
   
       ↓
7. Content Extraction
   - Title: Extract text from <h1> or <h2.article-title>
   - Content: Extract all text from <article>, <div.content>, <p>
   - Date: Extract from <time> or <span.date>
   
       ↓
8. Return Articles
   - List of ArticleContent objects
```

### Configuration File Structure

#### **config/sources.yaml** - Main Configuration

```yaml
sources:
  - name: "Source Display Name"           # Used in logs/UI
    base_url: "https://example.com"       # Base domain
    enabled: true/false                   # Enable/disable this source
    search_url_template: "URL with {query} placeholder"
    rate_limit: 3.0                       # Seconds between requests
    selectors:                            # CSS selectors for extraction
      article_links: "CSS selector"       # Find article URLs on search page
      title: "CSS selector"               # Extract article title
      content: "CSS selector"             # Extract article content
      date: "CSS selector"                # Extract publish date
      author: "CSS selector"              # Extract author (optional)
    headers:                              # HTTP headers for requests
      User-Agent: "..."
      Accept: "..."
```

### Understanding CSS Selectors

CSS selectors tell the scraper **where to find content** on a webpage.

#### Example HTML:
```html
<article>
  <h1 class="article-title">Kashmir Attack Kills 5</h1>
  <time datetime="2025-12-03">Dec 3, 2025</time>
  <div class="article-body">
    <p>A terrorist attack in Kashmir...</p>
    <p>Security forces responded...</p>
  </div>
</article>
```

#### Corresponding Selectors:
```yaml
selectors:
  title: "h1.article-title"        # Finds <h1 class="article-title">
  content: "div.article-body p"    # Finds all <p> inside <div class="article-body">
  date: "time"                     # Finds <time> tag
```

#### Common Selector Patterns:

| Pattern | Meaning | Example |
|---------|---------|---------|
| `tag` | Element by tag name | `h1`, `p`, `article` |
| `.class` | Element by class | `.article-title` |
| `#id` | Element by ID | `#main-heading` |
| `tag.class` | Tag with class | `h1.article-title` |
| `tag[attr]` | Tag with attribute | `a[href]` |
| `tag[attr='value']` | Exact attribute match | `a[href='/news']` |
| `tag[attr*='value']` | Attribute contains | `a[href*='article']` |
| `parent > child` | Direct child | `article > p` |
| `ancestor descendant` | Any descendant | `article p` |
| `selector1, selector2` | Multiple (OR) | `h1, h2` |

### Fallback Selectors

For sites with multiple page layouts:

```yaml
selectors:
  # Try first selector, if not found, try second, then third
  title: "h1#main-heading, h1.article-title, h1"
  content: "article[data-component='text-block'], div.content, p"
```

**How it works:**
1. Try to find `h1#main-heading`
2. If not found, try `h1.article-title`
3. If not found, try any `h1`
4. If none found, return empty

### Rate Limiting

```yaml
rate_limit: 3.0  # Wait 3 seconds between requests
```

**Why:**
- Prevent overwhelming the server
- Avoid getting blocked/banned
- Respect website's resources
- Academic/research sites need longer delays

**Calculation:**
```
20 articles × 3 seconds = 60 seconds = 1 minute
```

### How to Write a Config File

#### Step-by-Step Guide:

**1. Identify Target Website**
```
Example: https://www.satp.org
```

**2. Find Search URL**
```
Search for "terrorism" on the site
Observe URL: https://www.satp.org/terrorist-activity/southasia?search=terrorism
```

**3. Create Template**
```yaml
search_url_template: "https://www.satp.org/terrorist-activity/southasia?search={query}"
```
Replace actual query with `{query}` placeholder.

**4. Inspect Search Results Page**
```
Right-click → Inspect Element
Find article links
```

Example HTML:
```html
<a href="/terrorist-activity/india-2025">India Terrorism 2025</a>
<a href="/terrorist-activity/pakistan-2025">Pakistan Terrorism 2025</a>
```

**5. Determine article_links Selector**
```yaml
article_links: "a[href*='terrorist-activity']"
```
This finds all `<a>` tags with href containing "terrorist-activity".

**6. Visit One Article**
```
Open: https://www.satp.org/terrorist-activity/india-2025
```

**7. Inspect Article Structure**

Find title:
```html
<h1>India Terrorism Timeline 2025</h1>
```
Selector: `"h1"`

Find content:
```html
<article>
  <p>December 2: Attack in Kashmir...</p>
  <p>December 1: Encounter in Bihar...</p>
</article>
```
Selector: `"article p"` or `"article"`

Find date:
```html
<time datetime="2025-12-02">December 2, 2025</time>
```
Selector: `"time"`

**8. Write Complete Config**
```yaml
sources:
  - name: "SATP"
    base_url: "https://www.satp.org"
    enabled: true
    search_url_template: "https://www.satp.org/terrorist-activity/southasia?search={query}"
    rate_limit: 3.0
    selectors:
      article_links: "a[href*='terrorist-activity']"
      title: "h1"
      content: "article, p"
      date: "time"
    headers:
      User-Agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

**9. Test**
```
Search for: "Kashmir"
Check logs for successful scraping
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| No articles found | Check `article_links` selector on search page |
| Empty titles | Check `title` selector on article page |
| Empty content | Check `content` selector, try broader selector |
| Getting blocked | Increase `rate_limit` |
| Wrong articles | Make `article_links` selector more specific |
| Multiple page types | Use fallback selectors with commas |

---

## 2. spaCy NLP Processing

### Overview
spaCy is a **Natural Language Processing (NLP) library** that extracts structured information from unstructured text.

### What spaCy Does in This System

#### Step 1: Text Preprocessing
```python
# Input: Raw article text
text = "A terrorist attack in Srinagar, Kashmir killed 5 people on December 2, 2025."

# spaCy processing
doc = nlp(text)  # nlp = spacy.load("en_core_web_sm")
```

#### Step 2: Named Entity Recognition (NER)

spaCy automatically identifies:

| Entity Type | Example | Detected As |
|-------------|---------|-------------|
| **GPE** (Geo-Political Entity) | "Srinagar", "Kashmir" | LOCATION |
| **DATE** | "December 2, 2025" | DATE |
| **CARDINAL** | "5 people" | NUMBER |
| **ORG** (Organization) | "Lashkar-e-Taiba" | ORGANIZATION |
| **PERSON** | "Narendra Modi" | PERSON |
| **EVENT** | "Mumbai Attacks" | EVENT |

**Code Example:**
```python
doc = nlp("Attack in Srinagar, Kashmir on December 2, 2025")

for ent in doc.ents:
    print(f"{ent.text} → {ent.label_}")
    
# Output:
# Srinagar → GPE
# Kashmir → GPE
# December 2, 2025 → DATE
```

#### Step 3: Entity Extraction

**Location Extraction:**
```python
# From: "Terrorist attack in Srinagar, Jammu and Kashmir, India"
# Extracts:
{
    "city": "Srinagar",
    "region": "Jammu and Kashmir", 
    "country": "India"
}
```

**Date Extraction:**
```python
# From: "Attack occurred on December 2, 2025"
# Extracts: "2025-12-02"
```

**Organization Extraction:**
```python
# From: "Lashkar-e-Taiba claimed responsibility"
# Extracts: ["Lashkar-e-Taiba"]
```

### How spaCy Works Internally

#### 1. Tokenization
```
Text: "Kashmir attack kills 5"
Tokens: ["Kashmir", "attack", "kills", "5"]
```

#### 2. Part-of-Speech (POS) Tagging
```
Kashmir → PROPN (Proper Noun)
attack  → NOUN
kills   → VERB
5       → NUM (Number)
```

#### 3. Dependency Parsing
```
           kills (ROOT)
          /     \
    Kashmir    attack (subject)
                  \
                   5 (object)
```

#### 4. Named Entity Recognition
```
Kashmir → GPE (Geopolitical Entity)
5       → CARDINAL (Number)
```

### spaCy Models

**Current Model:** `en_core_web_sm`
- **Size:** ~12 MB
- **Components:** Tokenizer, Tagger, Parser, NER
- **Languages:** English
- **Accuracy:** ~85% on news text

**Alternative Models:**
```
en_core_web_md  - 40 MB, better accuracy
en_core_web_lg  - 560 MB, highest accuracy
en_core_web_trf - 438 MB, transformer-based (best)
```

### spaCy in the Pipeline

```
Article Text
     ↓
spaCy Processing
     ↓
Entities Extracted:
 - Locations: ["Srinagar", "Kashmir", "India"]
 - Dates: ["2025-12-02"]
 - Organizations: ["LeT"]
 - People: ["Terrorist leader XYZ"]
     ↓
Used by LLM for context
     ↓
Final Event Data
```

### Example: Full NER Pipeline

**Input Text:**
```
"On December 2, 2025, a terrorist attack in Srinagar, Jammu and Kashmir, 
killed 5 security personnel. Lashkar-e-Taiba claimed responsibility."
```

**spaCy Processing:**
```python
doc = nlp(text)

# Extract entities
locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
# → ["Srinagar", "Jammu and Kashmir"]

dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
# → ["December 2, 2025"]

orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
# → ["Lashkar-e-Taiba"]

numbers = [ent.text for ent in doc.ents if ent.label_ == "CARDINAL"]
# → ["5"]
```

**Structured Output:**
```python
{
    "locations": ["Srinagar", "Jammu and Kashmir"],
    "date": "2025-12-02",
    "organizations": ["Lashkar-e-Taiba"],
    "casualties": 5
}
```

### spaCy Confidence Scores

```python
for ent in doc.ents:
    print(f"{ent.text}: {ent.label_} (confidence: {ent._.confidence})")
```

Low confidence entities are filtered out (threshold: 0.5).

---

## 3. LLM Model Role

### Overview
The **LLM (Large Language Model)** is the "brain" that converts unstructured article text into structured event data.

### Current Model: Qwen 2.5 3B

**Specifications:**
- **Size:** ~2 GB
- **Parameters:** 3 billion
- **Context Window:** 32,768 tokens
- **Strengths:** 
  - Fast inference (~10-30 sec/article)
  - Excellent JSON generation
  - Good multilingual support (English + Asian languages)
  - Strong reasoning for event extraction

### What the LLM Does

#### Input: Article Text + Instructions

```
Article: "On December 2, 2025, a terrorist attack in Srinagar, Jammu and 
Kashmir, killed 5 Indian Army personnel. Lashkar-e-Taiba claimed responsibility. 
The attack involved an IED explosion followed by gunfire."

Instructions: Extract event information in JSON format with:
- event_type (attack/bombing/shooting/kidnapping/other)
- description (brief summary)
- location (city, region, country)
- date
- casualties
- organizations involved
- severity (1-10)
- confidence (0.0-1.0)
```

#### LLM Processing

The model:
1. **Reads and understands** the article
2. **Identifies key information**:
   - Event type: "attack" (combined IED + gunfire)
   - Location: Srinagar, Jammu and Kashmir, India
   - Date: December 2, 2025
   - Casualties: 5 killed (military)
   - Actor: Lashkar-e-Taiba
   - Severity: High (8/10 - military casualties)
3. **Generates structured JSON**

#### Output: Structured Event Data

```json
{
  "event_type": "attack",
  "description": "IED explosion followed by gunfire targeting Indian Army in Srinagar, Kashmir. 5 soldiers killed. LeT claimed responsibility.",
  "location": {
    "city": "Srinagar",
    "region": "Jammu and Kashmir",
    "country": "India",
    "coordinates": null
  },
  "date": "2025-12-02",
  "casualties": {
    "killed": 5,
    "injured": 0,
    "civilians": 0,
    "security_forces": 5
  },
  "actors": {
    "perpetrators": ["Lashkar-e-Taiba"],
    "targets": ["Indian Army"]
  },
  "event_details": {
    "attack_method": ["IED", "gunfire"],
    "weapons_used": ["explosive device", "firearms"]
  },
  "severity": 8,
  "confidence": 0.95,
  "source_reliability": "high"
}
```

### LLM vs spaCy: Division of Labor

| Task | Tool | Why |
|------|------|-----|
| **Entity extraction** | spaCy | Fast, deterministic, good for standard entities |
| **Event classification** | LLM | Requires reasoning (attack vs protest vs political event) |
| **Context understanding** | LLM | Understands narrative, relationships, intent |
| **JSON generation** | LLM | Flexible structure, handles edge cases |
| **Confidence scoring** | LLM | Assesses uncertainty based on article quality |
| **Severity assessment** | LLM | Requires judgment of impact/significance |

### LLM Prompt Engineering

The system uses a **carefully crafted prompt** to guide the LLM:

```python
prompt = f"""
Extract event information from this news article about terrorism/security incidents.

Article:
{article_content[:1500]}  # Truncated to 1500 chars for speed

Extract and return ONLY valid JSON with this structure:
{{
  "event_type": "attack|bombing|shooting|kidnapping|arrest|encounter|other",
  "description": "Brief summary (max 200 chars)",
  "location": {{"city": "...", "region": "...", "country": "..."}},
  "date": "YYYY-MM-DD or null",
  "severity": 1-10,
  "confidence": 0.0-1.0
}}

Rules:
- If not a terrorism/security event, return {{"event_type": "other", "confidence": 0.0}}
- Use null for unknown fields
- Date format: YYYY-MM-DD
- Description: factual, concise

JSON:
"""
```

### LLM Configuration

**backend/app/services/ollama_service.py:**
```python
options = {
    "temperature": 0.1,      # Low = deterministic, focused
    "num_ctx": 2048,         # Context window
    "top_k": 10,             # Limit sampling
    "top_p": 0.9,            # Nucleus sampling
    "num_predict": 300       # Max tokens to generate
}
```

**What these mean:**

| Parameter | Value | Effect |
|-----------|-------|--------|
| `temperature` | 0.1 | Very focused, deterministic output |
| `num_ctx` | 2048 | How much context to consider |
| `top_k` | 10 | Sample from top 10 most likely tokens |
| `top_p` | 0.9 | Nucleus sampling threshold |
| `num_predict` | 300 | Max JSON length |

**Temperature Scale:**
```
0.0 = Completely deterministic (same output every time)
0.1 = Very focused (current setting)
0.5 = Balanced
1.0 = Creative but unpredictable
2.0 = Chaotic, unusable for structured data
```

### LLM Performance Optimization

**1. Content Truncation**
```python
content = article_text[:1500]  # Only first 1500 chars
```
- **Why:** Faster processing, usually contains key info
- **Trade-off:** May miss details at end of article

**2. Shorter Prompts**
```python
prompt = short_template  # ~400 chars vs 1500+ original
```
- **Why:** Less tokens to process
- **Trade-off:** Less detailed instructions

**3. Token Limits**
```python
num_predict = 300  # Max output tokens
```
- **Why:** Prevents overly verbose responses
- **Trade-off:** Must be concise

**4. Aggressive Sampling**
```python
top_k = 10  # Only consider top 10 tokens
```
- **Why:** Faster decision making
- **Trade-off:** Less creative output (good for JSON!)

### LLM Error Handling

#### Common Errors:

**1. Invalid JSON**
```python
try:
    event_data = json.loads(llm_response)
except json.JSONDecodeError:
    # Retry with JSON repair or skip article
```

**2. Timeout**
```python
try:
    event_data = await asyncio.wait_for(
        llm_process(article),
        timeout=60  # 1 minute per article
    )
except asyncio.TimeoutError:
    # Skip article, log warning
```

**3. Malformed Response**
```python
if "event_type" not in event_data:
    # Response missing required fields
    # Use default values or skip
```

### Why LLM is Essential

**Without LLM:**
```
Article: "Militants attacked army base..."
spaCy: 
  - Entities: ["army base"]
  - Location: Unknown
  - Event type: Unknown
  - Severity: Unknown
Result: Useless
```

**With LLM:**
```
Article: "Militants attacked army base..."
LLM understands:
  - "Militants attacked" = terrorist attack
  - "army base" = military target
  - Context: High severity event
  - Extracts: location, casualties, actors
Result: Structured, actionable intelligence
```

### LLM Model Comparison

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **qwen2.5:3b** | 2 GB | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | **Production** ✅ |
| llama3.2:3b | 2 GB | ⚡⚡ Medium | ⭐⭐ Fair | Balanced |
| gemma3:1b | 815 MB | ⚡⚡⚡ Very Fast | ⭐⭐ Fair | Speed priority |
| llama3.1:8b | 4.9 GB | 🐌 Slow | ⭐⭐⭐⭐ Excellent | Quality priority |

---

## 4. Complete Workflow

### End-to-End Process

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                                │
│    Query: "Kashmir terrorism"                                │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CONFIGURATION LOADING                                     │
│    - Load sources.yaml                                       │
│    - Filter enabled sources: [SATP]                          │
│    - Get selectors for each source                           │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. WEB SCRAPING                                              │
│    For each source:                                          │
│      - Build search URL                                      │
│      - Send HTTP request                                     │
│      - Parse HTML with BeautifulSoup                         │
│      - Extract article links using selectors                 │
│      - Visit each article URL                                │
│      - Extract: title, content, date                         │
│    Result: 20 ArticleContent objects                         │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. SPACY NER PROCESSING                                      │
│    For each article:                                         │
│      - Run spaCy NER: doc = nlp(article.content)             │
│      - Extract entities:                                     │
│        * Locations (GPE): ["Srinagar", "Kashmir"]            │
│        * Dates: ["2025-12-02"]                               │
│        * Organizations: ["LeT"]                              │
│      - Add entities to article metadata                      │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. LLM EVENT EXTRACTION                                      │
│    For first 5 articles (OLLAMA_MAX_ARTICLES=5):             │
│      - Truncate content: article[:1500]                      │
│      - Build prompt with instructions                        │
│      - Send to LLM (qwen2.5:3b)                              │
│      - Receive JSON response                                 │
│      - Parse and validate JSON                               │
│      - Extract event data:                                   │
│        {                                                     │
│          event_type, description, location,                  │
│          date, severity, confidence                          │
│        }                                                     │
│      - Timeout if >60s per article                           │
│    Result: 5 EventData objects                               │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. QUERY MATCHING                                            │
│    For each extracted event:                                 │
│      - Calculate relevance score:                            │
│        * Text match: Query in description? (40%)             │
│        * Location match: Query in location? (25%)            │
│        * Date match: Recent? (20%)                           │
│        * Event type match: Relevant type? (15%)              │
│      - Filter events: score > 0.3                            │
│      - Sort by relevance score (descending)                  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. SESSION STORAGE                                           │
│    - Generate session ID                                     │
│    - Store events in memory cache                            │
│    - TTL: 1 hour                                             │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. RESPONSE TO USER                                          │
│    {                                                         │
│      "session_id": "abc-123",                                │
│      "query": {"phrase": "Kashmir terrorism"},               │
│      "events": [                                             │
│        {                                                     │
│          "event_type": "attack",                             │
│          "description": "IED attack in Srinagar...",         │
│          "location": {"city": "Srinagar", ...},              │
│          "severity": 8,                                      │
│          "confidence": 0.95,                                 │
│          "relevance_score": 0.92                             │
│        },                                                    │
│        ...                                                   │
│      ],                                                      │
│      "total_scraped": 20,                                    │
│      "total_processed": 5,                                   │
│      "total_matched": 3                                      │
│    }                                                         │
└─────────────────────────────────────────────────────────────┘
```

### Timing Breakdown

**For search: "Kashmir terrorism"**

| Step | Duration | Details |
|------|----------|---------|
| Config loading | <0.1s | Cached after first load |
| Web scraping | ~60s | 20 articles × 3s rate limit |
| spaCy NER | ~5s | 20 articles × 0.25s |
| LLM extraction | ~50s | 5 articles × 10s |
| Query matching | <1s | Vector similarity |
| **Total** | **~116s** | **~2 minutes** |

### Component Interactions

```
┌─────────────┐
│   User UI   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP POST /api/v1/search
       ↓
┌─────────────────────┐
│   Search Service    │
│   (Orchestrator)    │
└──┬────────┬────────┬┘
   │        │        │
   ↓        ↓        ↓
┌─────┐ ┌──────┐ ┌────────┐
│Web  │ │spaCy │ │ LLM    │
│Scrap│ │ NER  │ │Service │
└─────┘ └──────┘ └────────┘
   │        │        │
   ↓        ↓        ↓
┌─────────────────────┐
│ Content Extractor   │
│ Event Extractor     │
│ Query Matcher       │
└─────────────────────┘
```

---

## Summary

### 1. Web Scraper
- **Reads** `sources.yaml` config
- **Follows** CSS selectors to extract content
- **Respects** rate limits
- **Returns** raw articles

### 2. spaCy
- **Processes** article text
- **Extracts** named entities (locations, dates, orgs)
- **Provides** structured metadata
- **Fast** and deterministic

### 3. LLM
- **Understands** context and narrative
- **Converts** unstructured text → structured JSON
- **Assesses** severity and confidence
- **Generates** event descriptions

### Key Relationships

```
Config File → Controls Web Scraper → Provides Articles
                                           ↓
Articles → spaCy NER → Entities → Context for LLM
                                           ↓
Articles + Context → LLM → Structured Events → User
```

### Configuration Best Practices

1. **Start simple** - Test with one source first
2. **Use broad selectors** - Then refine
3. **Test incrementally** - One selector at a time
4. **Monitor rate limits** - Avoid getting blocked
5. **Check logs** - Debug scraping issues
6. **Validate output** - Ensure quality events

---

## Quick Reference

### Config File Location
```
config/sources.yaml
```

### Restart After Config Changes
```bash
# Backend auto-reloads (--reload flag)
# No restart needed!
```

### Test a Selector
```python
from bs4 import BeautifulSoup
html = """<h1 class="title">Test</h1>"""
soup = BeautifulSoup(html, 'html.parser')
title = soup.select_one("h1.title")
print(title.text)  # "Test"
```

### Monitor Scraping
```bash
# Check logs/app.log
tail -f logs/app.log
```

### Adjust LLM Speed
```python
# In backend/.env
OLLAMA_TIMEOUT=60          # Time per article
OLLAMA_MAX_ARTICLES=5      # Articles to process
OLLAMA_TOTAL_TIMEOUT=300   # Total time limit
```

---

**End of Guide**
