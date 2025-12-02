# Event Scraper & Analyzer - User Guide

**Version:** 1.0.0  
**Last Updated:** December 2, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Searching for Events](#searching-for-events)
4. [Understanding Results](#understanding-results)
5. [Exporting Data](#exporting-data)
6. [Tips & Best Practices](#tips--best-practices)
7. [FAQ](#faq)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

The Event Scraper & Analyzer is a web-based tool that helps you find and analyze news events from multiple sources. It uses advanced natural language processing (NLP) and AI to extract structured event information from news articles.

### What Can It Do?

- ✅ Search across multiple news sources simultaneously
- ✅ Extract event details (date, location, type, people involved)
- ✅ Filter by location, date range, and event type
- ✅ Rank results by relevance
- ✅ Export selected events to Excel
- ✅ Provide structured, actionable intelligence

### Who Is It For?

- **Researchers** - Tracking events for studies
- **Analysts** - Monitoring specific types of incidents
- **Journalists** - Finding related stories
- **Security Personnel** - Tracking security incidents
- **General Users** - Anyone researching events

---

## Getting Started

### Accessing the Application

1. **Open your web browser**
2. **Navigate to:** http://localhost:5173 (development) or https://yourdomain.com (production)
3. **You'll see the search form**

### System Requirements

- **Modern web browser:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **JavaScript enabled**
- **Stable internet connection**

---

## Searching for Events

### Basic Search

The simplest way to search:

1. **Enter a search phrase** in the main text box
   - Example: `"protest in Mumbai"`
   - Example: `"cyber attack on banks"`
   - Example: `"earthquake in Turkey"`

2. **Click the Search button**

3. **Wait for results** (typically 30-60 seconds)

### Advanced Filtering

Use optional filters to refine your search:

#### 1. Location Filter

**Purpose:** Narrow results to a specific geographic area

**Examples:**
- City: `Mumbai`
- State/Province: `California`
- Country: `India`
- Region: `Middle East`
- Virtual: `Online`

**How it works:**
- Searches event location field
- Partial matches accepted
- Case-insensitive

#### 2. Event Type Filter

**Purpose:** Find specific types of events

**Categories:**

**Violence & Security:**
- Protest
- Demonstration
- Attack
- Explosion
- Bombing
- Shooting
- Theft
- Kidnapping

**Cyber Events:**
- Cyber Attack
- Cyber Incident
- Data Breach

**Meetings & Conferences:**
- Conference
- Meeting
- Summit

**Disasters & Accidents:**
- Accident
- Natural Disaster

**Political & Military:**
- Election
- Political Event
- Military Operation

**Crisis Events:**
- Terrorist Activity
- Civil Unrest
- Humanitarian Crisis

**Other:**
- Other

#### 3. Date Range

**Purpose:** Limit results to a specific time period

**Options:**
- **Start Date:** Events on or after this date
- **End Date:** Events on or before this date
- **Both:** Events within the range

**Examples:**
- Last month: `2025-11-01` to `2025-11-30`
- Specific event: `2025-03-15` to `2025-03-15`
- Year to date: `2025-01-01` to `2025-12-31`

### Search Tips

**Be Specific:**
```
❌ "attack"
✅ "cyber attack on financial institutions"
```

**Use Relevant Keywords:**
```
❌ "something happened in Mumbai"
✅ "protest refinery workers Mumbai"
```

**Combine Filters:**
```
Phrase: "data breach"
Type: Data Breach
Date: Last 6 months
```

**Try Variations:**
```
Search 1: "protest refinery"
Search 2: "demonstration oil workers"
Search 3: "strike petroleum industry"
```

---

## Understanding Results

### Results Overview

After searching, you'll see:

**Statistics Bar:**
```
Found 12 matching events from 15 extracted events
(23 articles scraped). Processing time: 45.32s
```

- **Matching Events:** Events that fit your query
- **Extracted Events:** Total events found in articles
- **Articles Scraped:** Number of articles processed
- **Processing Time:** How long the search took

### Event Cards

Each result shows:

**Event Header:**
- ☑ **Checkbox:** Select for export
- **Title:** Event headline (clickable link to source)
- **[Type]:** Event category chip

**Event Details:**
- 📅 **Date:** When the event occurred
- 📍 **Location:** City, State/Province, Country
- 🏢 **Organizer:** Who organized/conducted it (if applicable)

**Description:**
- Brief summary of the event (2-4 sentences)

**Metadata:**
- **Relevance Score:** How well it matches your query (0-100%)
  - 🟢 Green: 70%+ (high relevance)
  - 🟠 Orange: 50-69% (medium relevance)
  - ⚪ Gray: <50% (low relevance)
- **Source:** Link to original article

### Sorting Results

Use the **Sort By** dropdown:

**Relevance (Default):**
- Highest relevance score first
- Best for finding most relevant events

**Date:**
- Earliest date first
- Best for chronological analysis

**Title:**
- Alphabetical order (A-Z)
- Best for scanning alphabetically

### Selecting Events

**Individual Selection:**
- Click the checkbox on each event card
- Or click anywhere on the card

**Select All:**
- Click the "Select All" button
- Selects all events on current page

**Clear Selection:**
- Click the "Clear" button
- Deselects all events

**Selection Indicator:**
- Blue alert shows: "X events selected for export"

---

## Exporting Data

### Export Options

**Export All Events:**
- Don't select any events
- Click "Export All to Excel"
- Downloads all matching events

**Export Selected Events:**
- Select desired events
- Click "Export X Selected to Excel"
- Downloads only selected events

### Excel File Structure

The exported file contains these columns:

| Column | Description |
|--------|-------------|
| Title | Event headline |
| Date | Event date (YYYY-MM-DD) |
| City | City name |
| State | State/Province |
| Country | Country name |
| Venue | Specific venue (if available) |
| Event Type | Category (protest, attack, etc.) |
| Description | Event summary |
| Organizer | Organizing entity |
| Relevance Score | Match score (0-100%) |
| Source URL | Link to original article |
| URL | Event-specific URL (if different) |

### File Naming

Files are automatically named:
```
events_{search_phrase}_{date}.xlsx
```

Example:
```
events_protest_in_Mumbai_2025-12-02.xlsx
```

### Opening the File

1. **Locate the download** in your Downloads folder
2. **Double-click** to open in Excel, LibreOffice, or Google Sheets
3. **Review and analyze** the data
4. **Further filtering** available in Excel

---

## Tips & Best Practices

### Search Strategy

**1. Start Broad, Then Narrow:**
```
Step 1: "cyber attack"          (100 results)
Step 2: Add type: Cyber Attack  (50 results)
Step 3: Add location: India     (12 results)
Step 4: Add date range          (5 results)
```

**2. Use Multiple Searches:**
```
Search different variations:
- "protest refinery"
- "demonstration oil workers"
- "strike petroleum"
```

**3. Check Different Date Ranges:**
```
- Last week
- Last month
- Last 6 months
- Specific event date
```

### Quality Results

**For Best Accuracy:**
- Use specific phrases (not single words)
- Include context keywords
- Use location filters when possible
- Verify important events with source links

**Interpreting Relevance:**
- ≥80%: Very likely relevant
- 60-79%: Probably relevant, verify
- 40-59%: Possibly relevant, check carefully
- <40%: May be false positive

### Performance

**Faster Searches:**
- Use more filters (narrows scope)
- Search recent dates (less data)
- Be specific in phrase

**More Comprehensive Results:**
- Use broader phrases
- Remove date filters
- Search "All Types"

**Finding More Events:**
```
If you get few results:
- Try synonyms
- Broaden location (country vs. city)
- Expand date range
- Remove event type filter
```

---

## FAQ

### General Questions

**Q: How long does a search take?**  
A: Typically 30-60 seconds, depending on:
- Number of sources configured
- Date range searched
- Complexity of query

**Q: How many sources are searched?**  
A: This depends on configuration. Check with your administrator.

**Q: Can I save searches?**  
A: Currently, searches are not saved. You must export results for future reference.

**Q: How recent are the articles?**  
A: This depends on when sources are scraped. Typically updated daily.

### Search Questions

**Q: Why am I getting few/no results?**  
A: Try:
- Broader search phrase
- Remove filters
- Expand date range
- Check spelling

**Q: Why are some results not relevant?**  
A: The AI does its best but isn't perfect. Use:
- More specific phrases
- Event type filter
- Check relevance scores
- Verify with source links

**Q: Can I search in other languages?**  
A: Currently, only English is supported.

**Q: What date format should I use?**  
A: YYYY-MM-DD (e.g., 2025-12-02)

### Export Questions

**Q: What format is the export?**  
A: Excel (.xlsx) format, compatible with Excel, LibreOffice, Google Sheets.

**Q: Can I export to CSV or JSON?**  
A: Currently, only Excel is supported.

**Q: Is there a limit on exported events?**  
A: Typically limited to 1000 events per export.

**Q: Can I customize export columns?**  
A: Currently, all columns are exported. You can hide unwanted columns in Excel.

### Technical Questions

**Q: Why is it slow?**  
A: Factors:
- Analyzing many articles
- Complex AI processing
- Network speed
- Server load

**Q: Will it work on mobile?**  
A: Yes, but desktop is recommended for better experience.

**Q: Is my search data saved?**  
A: Searches are temporarily stored for the session but not permanently saved.

**Q: Is there an API?**  
A: Yes, see [API Documentation](API.md) for developers.

---

## Troubleshooting

### Common Issues

#### "Cannot connect to server"

**Cause:** Backend not running or network issue

**Solution:**
1. Check if backend server is running
2. Verify URL in browser
3. Check firewall/network settings
4. Contact administrator

#### "Please enter a search phrase"

**Cause:** Empty search field

**Solution:**
- Enter at least one keyword

#### "Start date must be before end date"

**Cause:** Invalid date range

**Solution:**
- Verify dates are in correct order
- Check date format (YYYY-MM-DD)

#### "No events found"

**Cause:** No matching events in sources

**Solution:**
- Try broader search
- Expand date range
- Remove filters
- Try different keywords

#### "Export failed"

**Cause:** Server error or network issue

**Solution:**
1. Try again
2. Check if events are selected
3. Verify network connection
4. Contact administrator if persists

#### Search takes very long (>2 minutes)

**Possible causes:**
- Many sources configured
- Broad date range
- Slow network
- Server overload

**Solution:**
- Wait for completion
- Try narrower search
- Use more filters
- Contact administrator

#### Results don't match my query

**Review:**
- Check relevance scores
- Verify event descriptions
- Use more specific phrases
- Add event type filter
- Check source articles

### Getting Help

**Contact Support:**
- Email: support@yourdomain.com
- Documentation: [Online Docs]
- GitHub Issues: [Report Bug]

**Include in Support Request:**
1. Search phrase used
2. Filters applied
3. Error message (if any)
4. Browser and version
5. Screenshot (if helpful)

---

## Appendix

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Focus search box | Alt+S |
| Submit search | Enter (in search box) |
| Select all | Ctrl+A (in results) |
| Export | Alt+E |

### Glossary

**Event:** A specific occurrence (protest, attack, conference, etc.)

**Relevance Score:** Measure of how well an event matches your query (0-100%)

**Scraping:** Automated extraction of data from websites

**NER (Named Entity Recognition):** AI technique to identify people, places, organizations

**LLM (Large Language Model):** AI system used for understanding and extracting information

**Session:** Temporary storage of your search results

---

## Version History

**v1.0.0** (December 2, 2025)
- Initial release
- Search functionality
- Event type filtering
- Excel export
- Multi-source scraping

---

**Need more help?** Contact support@yourdomain.com

**End of User Guide**
