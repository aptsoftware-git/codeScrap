# Event Details Modal - Field Specification

## Updated Field Order and Headings (December 7, 2025)

This document specifies the **exact field order and headings** for the Event Details modal based on user requirements.

---

## Field Display Order

The Event Details modal displays fields in this **exact order**:

### 1. **Event Time**
- **Backend Field**: `event_time`
- **Display**: Time of occurrence (if available)
- **Format**: Text (e.g., "10:30 AM", "morning", "evening")
- **Show if**: Field has value
- **Example**: "10:30 AM"

### 2. **Event Type**
- **Backend Field**: `event_type`
- **Display**: Primary classification
- **Format**: Color-coded chip
  - Red: bombing, shooting, attack, terrorism
  - Yellow: riot, violence, civil unrest
  - Blue: protest, demonstration, march
  - Green: other events
- **Show if**: Always (required field)
- **Example**: "bombing" (red chip)

### 3. **Event Sub-Type** ⚠️
- **Backend Field**: NOT AVAILABLE YET
- **Display**: Secondary classification (if applicable)
- **Status**: **Commented out** - Needs backend implementation
- **Future**: Will show sub-categories like "suicide bombing", "mass shooting", etc.

### 4. **Event Title**
- **Backend Field**: `title`
- **Display**: Brief headline
- **Format**: Plain text
- **Show if**: Always (required field)
- **Example**: "2023 Kabul airport bombing"

### 5. **Event Summary**
- **Backend Field**: `summary`
- **Display**: 2-4 sentence description
- **Format**: Plain text
- **Show if**: Always (required field)
- **Example**: "A bombing occurred at a checkpoint outside the military airport in Kabul, Afghanistan on January 1, 2023."

### 6. **Perpetrator**
- **Backend Field**: `perpetrator`
- **Display**: Individual or group attribution
- **Format**: Plain text
- **Show if**: Field has value, else "N/A"
- **Example**: "Islamic State"
- **Note**: Falls back to `organizer` for backward compatibility

### 7. **Perpetrator Type** ⚠️
- **Backend Field**: NOT AVAILABLE YET
- **Display**: Classification (terrorist group, state actor, unknown, etc.)
- **Status**: **Commented out** - Needs backend implementation
- **Future**: Will categorize perpetrators (e.g., "Terrorist Group", "State Actor", "Individual", "Unknown")

### 8. **Location (Full)**
- **Backend Fields**: `location.venue`, `location.city`, `location.state`, `location.country`
- **Display**: Complete location string as extracted
- **Format**: Comma-separated: "venue, city, state, country"
- **Show if**: Always (required field)
- **Example**: "Kabul International Airport, Kabul, Afghanistan"

### 9. **City/Town**
- **Backend Field**: `location.city`
- **Display**: Parsed city name
- **Format**: Plain text
- **Show if**: Field has value
- **Example**: "Kabul"

### 10. **State/Province**
- **Backend Field**: `location.state`
- **Display**: Parsed administrative division
- **Format**: Plain text
- **Show if**: Field has value
- **Example**: "Kabul Province"

### 11. **Country**
- **Backend Field**: `location.country`
- **Display**: Parsed or source-attributed country
- **Format**: Plain text
- **Show if**: Field has value
- **Example**: "Afghanistan"

### 12. **Individuals Involved**
- **Backend Field**: `participants`
- **Display**: Comma-separated list of named persons
- **Format**: Plain text (comma-separated)
- **Show if**: Array has items
- **Example**: "John Doe, Jane Smith, Ahmad Khan"
- **Note**: Previously labeled "Participants"

### 13. **Organizations Involved**
- **Backend Field**: `organizations`
- **Display**: Comma-separated list of named organizations
- **Format**: Plain text (comma-separated)
- **Show if**: Array has items
- **Example**: "Islamic State, Taliban, Afghan National Army"
- **Note**: Previously labeled "Organizations"

### 14. **Casualties**
- **Backend Field**: `casualties.killed`, `casualties.injured`
- **Display**: Fatalities and injuries (if reported)
- **Format**: Color-coded chips
  - Red chip: "Killed: 5"
  - Yellow chip: "Injured: 12"
- **Show if**: Either killed or injured has value
- **Example**: "Killed: 5" (red) + "Injured: 12" (yellow)

### 15. **Source Name**
- **Backend Field**: `source_name`
- **Display**: Publication or website name
- **Format**: Plain text
- **Show if**: Field has value
- **Example**: "DuckDuckGo", "BBC News", "Reuters"

### 16. **Source URL**
- **Backend Field**: `source_url`
- **Display**: Direct link to original article
- **Format**: Clickable hyperlink (opens in new tab)
- **Show if**: Always (shows "N/A" if missing)
- **Example**: https://en.wikipedia.org/wiki/2023_Kabul_airport_bombing

### 17. **Publication Date**
- **Backend Field**: `article_published_date`
- **Display**: When article was published
- **Format**: Formatted date/time (e.g., "January 1st, 2023 12:00 AM")
- **Show if**: Field has value
- **Example**: "January 1st, 2023 12:00 AM"
- **Note**: Previously labeled "Article Published"

### 18. **Event Date**
- **Backend Field**: `event_date`
- **Display**: When event occurred
- **Format**: Formatted date/time (e.g., "January 1st, 2023 12:00 AM")
- **Show if**: Always
- **Example**: "January 1st, 2023 12:00 AM"
- **Note**: Falls back to `date` for backward compatibility

### 19. **Extraction Confidence**
- **Backend Field**: `confidence`
- **Display**: Overall confidence score (%)
- **Format**: Color-coded chip
  - Green: ≥80% (high confidence)
  - Yellow: 60-79% (medium confidence)
  - Red: <60% (low confidence)
- **Show if**: Always (required field)
- **Example**: "85%" (green chip)
- **Note**: Previously labeled "Confidence Score"

### 20. **Collection Timestamp** ⚠️
- **Backend Field**: NOT AVAILABLE YET
- **Display**: When system retrieved the content
- **Status**: **Commented out** - Needs backend implementation
- **Future**: Will show when article was scraped/collected
- **Example**: "December 7, 2025 3:45 PM"

### 21. **Full Content**
- **Backend Field**: `full_content`
- **Display**: Complete article text
- **Format**: Scrollable text box (max height 200px, gray background)
- **Show if**: Field has value
- **Example**: Full Wikipedia article text

---

## Fields REMOVED

### ❌ Impact
- **Reason**: Duplicate of Event Summary
- **User Request**: "Impact is not required as it is same as event title"
- **Backend Field**: `impact` (still exists in backend, just not displayed)

### ❌ Relevance Score
- **Reason**: Not part of core event data (added by matcher service)
- **Backend Field**: `relevance_score` (still in interface, just not in details modal)
- **Note**: Still shown on event cards as a chip

---

## Fields PENDING Backend Implementation

These fields are **commented out** in the modal until backend support is added:

1. **Event Sub-Type** - Secondary event classification
2. **Perpetrator Type** - Categorization of perpetrator
3. **Collection Timestamp** - When system collected the data

To implement these fields:
1. Update `backend/app/models.py` - Add fields to `EventData` class
2. Update `frontend/src/types/events.ts` - Add fields to interface
3. Update LLM prompt to extract these fields
4. Uncomment rows in `EventDetailsModal.tsx`

---

## Example Event Details Display

```
┌────────────────────────────────────────────────────┐
│ Event Details                               [X]    │
├────────────────────────────────────────────────────┤
│ Event Time            │ 10:30 AM                   │
│ Event Type            │ [bombing] (red chip)       │
│ Event Title           │ 2023 Kabul airport bombing │
│ Event Summary         │ A bombing occurred at...   │
│ Perpetrator           │ Islamic State              │
│ Location (Full)       │ Kabul, Afghanistan         │
│ City/Town             │ Kabul                      │
│ Country               │ Afghanistan                │
│ Organizations Involved│ Islamic State, Taliban     │
│ Casualties            │ [Killed: 5] [Injured: 12]  │
│ Source Name           │ DuckDuckGo                 │
│ Source URL            │ https://en.wikipedia...    │
│ Publication Date      │ January 1st, 2023 12:00 AM │
│ Event Date            │ January 1st, 2023 12:00 AM │
│ Extraction Confidence │ [85%] (green chip)         │
│ Full Content          │ ┌────────────────┐         │
│                       │ │ Scrollable box │         │
│                       │ │ with full text │         │
│                       │ └────────────────┘         │
└────────────────────────────────────────────────────┘
```

---

## Backend Model Reference

Current `EventData` model structure:

```python
class EventData(BaseModel):
    event_type: EventType  # ✅ Available
    title: str  # ✅ Available
    summary: str  # ✅ Available
    perpetrator: Optional[str] = None  # ✅ Available
    location: Location  # ✅ Available (city, state, country, venue)
    event_date: Optional[datetime] = None  # ✅ Available
    event_time: Optional[str] = None  # ✅ Available
    participants: List[str] = []  # ✅ Available
    organizations: List[str] = []  # ✅ Available
    casualties: Optional[Dict[str, int]] = None  # ✅ Available
    impact: Optional[str] = None  # ✅ Available (not displayed)
    source_name: Optional[str] = None  # ✅ Available
    source_url: Optional[str] = None  # ✅ Available
    article_published_date: Optional[datetime] = None  # ✅ Available
    confidence: float  # ✅ Available
    full_content: Optional[str] = None  # ✅ Available
    
    # MISSING (need to add):
    # event_sub_type: Optional[str] = None
    # perpetrator_type: Optional[str] = None
    # collection_timestamp: Optional[datetime] = None
```

---

## Questions for User

Before implementing the missing backend fields, please confirm:

1. **Event Sub-Type**: 
   - Should this be a free-text field or predefined enum?
   - Examples: "suicide bombing", "vehicle attack", "mass shooting"
   - Should LLM extract this or should it be rule-based?

2. **Perpetrator Type**:
   - Predefined categories? (e.g., "Terrorist Group", "State Actor", "Individual", "Criminal Organization", "Unknown")
   - Should LLM classify or use rule-based matching?

3. **Collection Timestamp**:
   - Use article scrape time or current timestamp?
   - Should this be in `Event` model or `EventData` model?
   - Timezone preference (UTC or local)?

Please let me know your preferences and I can implement these fields!
