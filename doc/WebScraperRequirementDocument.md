# Software Requirements Specification

## Event-Focused Web Scraping, Summarization & Export Tool

---

## 1. Purpose and Scope

This application will:

- Visit a configurable list of URLs (news / blog / report sites)
- Scrape content from those pages
- Identify and summarize events relevant to a user-supplied phrase (e.g., "bomb blast in Kabul", "cyber attack in Europe between Jan and Mar 2024")
- Display these summaries as a list on a web page, each with:
  - Title
  - Short text summary
  - Link to the original article/source
- Allow the user to select one or more summaries and export them to Excel, with structured fields:
  - Type of event
  - Perpetrator
  - Location
  - Time
  - Individuals/organizations involved

The application is meant as an internal analysis / research tool, not for public, high-traffic use (at least in v1).

---

## 2. Stakeholders and Users

### Primary User
Analyst / researcher who:
- Defines the query phrase and time/location constraints
- Triggers the scraping + summarization
- Reviews summaries and exports selected items

### Administrator / Developer
- Configures list of URLs/sites
- Manages credentials (if any), scraping rules, and schedules
- Monitors logs and error reports

---

## 3. Assumptions & Constraints

### 3.1 Assumptions

- Target websites are publicly accessible (no login or paywall) or credentials are available if needed
- The number of target sites is moderate (e.g., 10–100 sources to start)
- The user's phrase is free-text; the system will attempt to interpret:
  - Event type (e.g., protest, attack, conference, accident)
  - Location (city, region, country)
  - Time or time range
- The system will use some form of NLP / NER (Named Entity Recognition) / rules / LLM to:
  - Extract entities (people, organizations, locations, dates)
  - Classify event type and perpetrator as best-effort

### 3.2 Constraints

- Scraping must respect robots.txt, site ToS, and rate limits
- The system must avoid overloading any site (configurable delay between requests per domain)
- Technologies:
  - **Backend:** Developer can choose (e.g., Python, Node.js, etc.), but code should be modular and testable
  - **Frontend:** Web-based UI (HTML/JS/CSS; framework choice is flexible)
  - **Export format:** Excel (.xlsx)

---

## 4. High-Level Overview

### 4.1 System Components

#### Web Scraper
- Fetches pages from configured URLs
- Extracts page content (title, publish date, main body text)
- Pluggable per-site extraction rules for complex sites

#### Event Extraction & Summarization Engine
- Filters text based on user query phrase and constraints
- Identifies candidate event descriptions within articles
- Summarizes each relevant event
- Extracts structured fields:
  - Event type
  - Perpetrator
  - Location
  - Time
  - Individuals / organizations

#### Web UI
- Form to input search phrase and filters
- Shows list of matching event summaries
- Allows selection (checkbox) and Excel export

#### Persistence Layer (Optional but Recommended)
Stores:
- Raw scraped articles (URL, date, content)
- Parsed events and metadata
- Query history (for debugging / reuse)

#### Export Service
- Generates Excel with selected events and fields

---

## 5. Detailed Functional Requirements

### 5.1 URL Management

**FR-1:** The system shall maintain a configurable list of source URLs and/or site patterns.

- **FR-1.1:** Admin can configure:
  - Static list of URLs
  - Base domains with path patterns (e.g., `https://example.com/news/*`)
- **FR-1.2:** The configuration shall support:
  - Human-readable name for the source
  - Optional category / tag (e.g., "Region: Middle East", "Topic: Cybersecurity")
- **FR-1.3:** Admin should be able to enable/disable individual sources without deleting them (even if this is just config for v1)

### 5.2 Scraping

**FR-2:** The system shall retrieve HTML pages from configured URLs.

- **FR-2.1:** Support HTTP(S)
- **FR-2.2:** Respect robots.txt and site ToS where feasible
- **FR-2.3:** Implement configurable rate limiting per domain (e.g., min N seconds between requests)
- **FR-2.4:** Handle HTTP failures gracefully:
  - Retry limited number of times
  - Log failures with status code and error message

**FR-3:** The system shall extract key data from each page:

- **FR-3.1:** Extract:
  - Page URL
  - Page title
  - Publication date (if available)
  - Main article text
- **FR-3.2:** For each site, allow pluggable parsing:
  - Generic extractor (e.g., boilerplate removal)
  - Site-specific rules (CSS selectors / XPath) for better accuracy

**FR-4:** The system shall deduplicate content.

- **FR-4.1:** Avoid storing/processing the same article multiple times (e.g., based on URL hash and publication date)

### 5.3 Query Input and Filtering

**FR-5:** The user shall be able to input a search phrase describing the event.

Example phrases:
- "protest near refinery in Gujarat last week"
- "bombing in Kabul in January 2023"
- "data breach events in Europe between March and May 2024"

**FR-6:** The UI shall also provide optional structured filters:

- **FR-6.1:** Time filters:
  - Single date (e.g., 2023-01-15)
  - Date range (From / To)
  - Relative (last 24 hours, last 7 days, last 30 days)
- **FR-6.2:** Location:
  - Free-text field (e.g., city, region, or country)
- **FR-6.3:** Event type (optional dropdown):
  - E.g., "Protest", "Attack", "Accident", "Cyber incident", "Conference", "Other"
- **FR-6.4:** These structured filters should constrain the results in addition to the free-text phrase

### 5.4 Event Detection and Matching

**FR-7:** The system shall process each article's text to identify potential event descriptions.

- **FR-7.1:** Use NLP / pattern-based methods to:
  - Detect sentences or paragraphs describing events
  - Extract candidate events (one article may contain multiple events, but v1 can assume typically one major event per article if needed)

**FR-8:** The system shall match events against user query and filters.

- **FR-8.1:** Relevance scoring:
  - Compute a relevance score based on:
    - Keyword match to phrase
    - Match on time constraints
    - Match on location
    - Match on event type (if specified)
- **FR-8.2:** Events with score below a threshold should be filtered out
- **FR-8.3:** Provide a way to sort events by:
  - Relevance score (default)
  - Publication date
  - Event date

### 5.5 Summarization

**FR-9:** For each matched event, the system shall generate a concise summary.

- **FR-9.1:** Summary fields:
  - **Title:** Either the article title or a generated event-specific title
  - **Summary text:** 2–4 sentences summarizing:
    - What happened
    - Where
    - When
    - Who was involved
    - (If available) perpetrator / responsible entity
- **FR-9.2:** Include the source URL
- **FR-9.3:** Limit summary length:
  - Title: max ~120 characters
  - Summary: max ~800 characters (configurable)

### 5.6 Structured Event Extraction

**FR-10:** For each event, the system shall attempt to extract structured fields:

- **Type of event** (classification)
  - E.g., protest, explosion, cyber attack, theft, demonstration, meeting, etc.
- **Perpetrator** (if applicable)
  - Individual name, group, or organization responsible (best-effort; can be Unknown)
- **Location**
  - City, region, country. Prefer storing standardized forms (e.g., city as separate field)
- **Time**
  - Date (mandatory if detected)
  - Time of day (optional if present)
  - If only a range is given (e.g., "between Monday and Wednesday"), store it as start & end date if possible
- **Individuals or organizations involved**
  - List of named people and organizations (NLP NER)
  - May include:
    - Victims
    - Authorities
    - Companies
    - NGOs, etc.

**FR-11:** Confidence scores (optional but useful).

- **FR-11.1:** For each extracted field, store an internal confidence score (0–1)
- **FR-11.2:** In v1 UI, it's sufficient to show the extracted value; confidence can be used internally or optionally shown as a small indicator

### 5.7 Web UI for Viewing Results

**FR-12:** The UI shall present a results page with a list of summarized events.

- **FR-12.1:** Each event item should show:
  - Checkbox for selection
  - Event title
  - Short summary text
  - Event date/time
  - Location
  - Source name and clickable source URL (opens in new tab)
- **FR-12.2:** Provide basic filtering/sorting within results:
  - Filter by event type
  - Filter by location
  - Sort by date or relevance
- **FR-12.3:** Pagination:
  - If results exceed a configurable limit (e.g., 50 per page), paginate

**FR-13:** The user should be able to select events:

- **FR-13.1:** Select individual events via checkbox
- **FR-13.2:** "Select all on page" option
- **FR-13.3:** Clear selection button

### 5.8 Excel Export

**FR-14:** The system shall provide an "Export to Excel" button.

- **FR-14.1:** Export only selected events; if none are selected, show a warning or prompt
- **FR-14.2:** Excel file (.xlsx) must contain at least the following columns:
  - Event Title
  - Summary
  - Event Type
  - Perpetrator
  - Location (full text)
  - City (if parsed)
  - Region/State (if parsed)
  - Country (if parsed)
  - Event Date
  - Event Time (if available)
  - Individuals Involved (comma-separated list)
  - Organizations Involved (comma-separated list)
  - Source Name
  - Source URL
  - Article Publication Date
  - Extraction Confidence (optional: could be average or JSON string)
- **FR-14.3:** File should be downloadable via the browser (save dialog)

### 5.9 Logging & Monitoring

**FR-15:** The system shall log:

- **FR-15.1:** Scraping actions:
  - Timestamp, URL, status (success/fail), response time, HTTP code
- **FR-15.2:** Errors in scraping or parsing:
  - Stack traces, messages (at least to server logs)
- **FR-15.3:** Query actions:
  - User query phrase
  - Number of events returned
  - Time taken

---

## 6. Non-Functional Requirements

### 6.1 Performance

- **NFR-1:** For a typical query over ~50–100 articles, initial results should be available within a reasonable time (e.g., < 20–30 seconds, depending on scraping model)
- **NFR-2:** If scraping is slow, design should allow:
  - Asynchronous scraping / background jobs
  - Displaying progress or partial results (future enhancement; v1 can be synchronous)

### 6.2 Scalability

- **NFR-3:** Architecture should allow adding:
  - More sources
  - Batch/scheduled scraping (e.g., nightly)
- **NFR-4:** Core logic (scraping, NLP, summarization) must be modular and reusable

### 6.3 Security

- **NFR-5:** If the app is deployed on a network:
  - Basic authentication or access control is recommended
- **NFR-6:** Any credentials for private sources must be stored securely (not in code)

### 6.4 Maintainability

- **NFR-7:** Site-specific scrapers / extraction logic must be clearly separated from core logic to simplify updates when site structures change
- **NFR-8:** Unit tests for:
  - Parsing / extraction from sample HTML
  - Entity extraction and classification on test texts
  - Excel export

---

## 7. Possible Technical Approach

*(This section is just guidance for the developer; you can adjust or remove.)*

- **Backend:**
  - Python with requests, httpx or similar, BeautifulSoup / lxml, and an NLP framework (spaCy, transformers, or an LLM API)
- **NLP / Extraction:**
  - Named entity recognition (people, orgs, location, dates)
  - Custom classification model or rules to classify event type
- **Frontend:**
  - Simple React/Vue/Angular or even server-rendered templates
- **Excel Export:**
  - Python's openpyxl / xlsxwriter (or equivalent in other languages)
- **Storage:**
  - Relational DB (PostgreSQL/MySQL) or document DB (MongoDB) for saved articles and events

---

## 8. Future Enhancements

*(Out of Scope for v1 but Consider Design Hooks)*

- User accounts with saved queries and dashboards
- Scheduler to scrape periodically and notify on new matching events
- Editing of extracted structured data via UI before export
- Multi-language support for non-English sources
- Visualization (maps/timelines) of events

---

## 9. UI Wireframes

### 9.1 Search Page

```
+--------------------------------------------------------------+
| EVENT SCRAPER                                                |
+--------------------------------------------------------------+
| Search Phrase: [___________________________________________] |
|                                                              |
| Time Filter: ( ) Any                                         |
|              ( ) Single Date [________]                      |
|              ( ) Range From [____] To [____]                 |
|                                                              |
| Relative Time: [ Last 7 Days ▼ ]                            |
| Location: [___________________________]                      |
| Event Type: [ Any ▼ ]                                        |
|                                                              |
| [ RUN SEARCH ]                                               |
+--------------------------------------------------------------+
```

### 9.2 Results Page

```
+--------------------------------------------------------------+
| EVENT SCRAPER                                   [New Search] |
+--------------------------------------------------------------+
| Filters: Type [Any ▼] Location [______] Sort [Relevance ▼]  |
+--------------------------------------------------------------+
| [ ] Select all                                               |
+--------------------------------------------------------------+
| [ ] Protest near refinery in Gujarat                         |
|     Date: 2025-03-12                                         |
|     Location: Jamnagar, India                                |
|     Summary: Short 2–4 sentence summary describing event...  |
|     Source: ExampleNews [View Article]                       |
+--------------------------------------------------------------+
| [ ] Cyber attack on regional bank in Mumbai                  |
|     Date: 2025-03-10                                         |
|     Location: Mumbai, India                                  |
|     Summary: Short summary...                                |
|     Source: CyberDaily [View Article]                        |
+--------------------------------------------------------------+
| Page 1 of 5    [Prev] [1] [2] [3] [Next]                    |
+--------------------------------------------------------------+
| [ EXPORT SELECTED TO EXCEL ]                                 |
+--------------------------------------------------------------+
```

---

## Document Information

**Version:** 1.0  
**Last Updated:** November 2025  
**Status:** Draft