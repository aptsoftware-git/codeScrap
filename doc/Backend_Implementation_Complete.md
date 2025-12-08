# Backend Implementation Complete - New Event Fields

## Date: December 7, 2025

## Summary

Successfully implemented backend support for 3 additional event fields requested by the user:

1. **Event Sub-Type** - Secondary classification (e.g., "suicide bombing", "mass shooting")
2. **Perpetrator Type** - Classification of perpetrator (terrorist group, state actor, individual, etc.)
3. **Collection Timestamp** - When the system collected/scraped the content

---

## Changes Made

### 1. Backend Model Updates

#### File: `backend/app/models.py`

**Added PerpetratorType Enum:**
```python
class PerpetratorType(str, Enum):
    """Classification of perpetrator types."""
    TERRORIST_GROUP = "terrorist_group"
    STATE_ACTOR = "state_actor"
    CRIMINAL_ORGANIZATION = "criminal_organization"
    INDIVIDUAL = "individual"
    MULTIPLE_PARTIES = "multiple_parties"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
```

**Updated EventData Model:**
```python
class EventData(BaseModel):
    event_type: EventType
    event_sub_type: Optional[str] = None  # NEW: Secondary classification
    title: str
    summary: str
    
    perpetrator: Optional[str] = None
    perpetrator_type: Optional[PerpetratorType] = None  # NEW: Perpetrator classification
    
    # ... other fields ...
    
    collection_timestamp: Optional[datetime] = None  # NEW: When system collected content
```

---

### 2. LLM Extraction Prompt Updates

#### File: `backend/app/services/event_extractor.py`

**Updated Prompt to Extract New Fields:**
- Added instructions for `event_sub_type` extraction
- Added instructions for `perpetrator_type` classification
- Updated JSON example to include new fields
- Added PERPETRATOR TYPES enum list for LLM reference

**Example JSON Output:**
```json
{
    "event_type": "bombing",
    "event_sub_type": "suicide bombing",  // NEW
    "perpetrator": "Islamic State",
    "perpetrator_type": "terrorist_group",  // NEW
    // ... other fields
}
```

---

### 3. Validation Logic

#### File: `backend/app/services/event_extractor.py`

**Added Perpetrator Type Validation Function:**
```python
def validate_perpetrator_type(self, perpetrator_type: str) -> Optional[PerpetratorType]:
    """
    Validate and normalize perpetrator type with fuzzy matching.
    
    Supports:
    - Exact matches
    - Fuzzy matching (handles spaces, underscores, hyphens)
    - Keyword-based classification
    - Smart defaults (unknown if unidentified)
    """
```

**Matching Logic:**
- Exact enum value matching
- Fuzzy string matching
- Keyword detection:
  - "terror", "militant" → TERRORIST_GROUP
  - "state", "government", "military" → STATE_ACTOR
  - "criminal", "gang", "cartel" → CRIMINAL_ORGANIZATION
  - "person", "individual", "man", "woman" → INDIVIDUAL
  - "multiple", "several" → MULTIPLE_PARTIES
  - "unknown", "unidentified" → UNKNOWN

---

### 4. Event Data Creation

#### File: `backend/app/services/event_extractor.py`

**Updated EventData Creation:**
```python
event_data = EventData(
    event_type=self.validate_event_type(parsed_data.get("event_type", "other")),
    event_sub_type=parsed_data.get("event_sub_type"),  # NEW
    perpetrator=perpetrator,
    perpetrator_type=self.validate_perpetrator_type(parsed_data.get("perpetrator_type")),  # NEW
    collection_timestamp=datetime.utcnow(),  # NEW: Capture scrape time
    # ... other fields
)
```

---

### 5. Frontend TypeScript Interface

#### File: `frontend/src/types/events.ts`

**Updated EventData Interface:**
```typescript
export interface EventData {
  event_type: EventType;
  event_sub_type?: string;  // NEW
  perpetrator?: string;
  perpetrator_type?: string;  // NEW
  collection_timestamp?: string;  // NEW
  // ... other fields
}
```

---

### 6. Frontend Event Details Modal

#### File: `frontend/src/components/EventDetailsModal.tsx`

**Uncommented and Activated New Fields:**

1. **Event Sub-Type** (after Event Type):
   ```tsx
   {event.event_sub_type && (
     <TableRow>
       <TableCell sx={{ fontWeight: 'bold' }}>Event Sub-Type</TableCell>
       <TableCell>{event.event_sub_type}</TableCell>
     </TableRow>
   )}
   ```

2. **Perpetrator Type** (after Perpetrator):
   ```tsx
   {event.perpetrator_type && (
     <TableRow>
       <TableCell sx={{ fontWeight: 'bold' }}>Perpetrator Type</TableCell>
       <TableCell>{formatPerpetratorType(event.perpetrator_type)}</TableCell>
     </TableRow>
   )}
   ```

3. **Collection Timestamp** (after Extraction Confidence):
   ```tsx
   {event.collection_timestamp && (
     <TableRow>
       <TableCell sx={{ fontWeight: 'bold' }}>Collection Timestamp</TableCell>
       <TableCell>{formatDate(event.collection_timestamp)}</TableCell>
     </TableRow>
   )}
   ```

**Added Helper Function:**
```typescript
const formatPerpetratorType = (type: string | undefined): string => {
  if (!type) return '';
  // Convert snake_case to Title Case
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};
```

---

## Field Specifications

### Event Sub-Type
- **Type**: Optional string (free-text)
- **Purpose**: More specific event classification
- **Examples**:
  - "suicide bombing"
  - "vehicle attack"
  - "mass shooting"
  - "targeted assassination"
  - "improvised explosive device (IED)"
- **Extracted by**: LLM from article content
- **Display**: Plain text (if available)

### Perpetrator Type
- **Type**: Optional PerpetratorType enum
- **Purpose**: Classify the nature of the perpetrator
- **Values**:
  - `terrorist_group` → "Terrorist Group"
  - `state_actor` → "State Actor"
  - `criminal_organization` → "Criminal Organization"
  - `individual` → "Individual"
  - `multiple_parties` → "Multiple Parties"
  - `unknown` → "Unknown"
  - `not_applicable` → "Not Applicable"
- **Extracted by**: LLM classification with fallback validation
- **Display**: Title Case conversion (e.g., "terrorist_group" → "Terrorist Group")

### Collection Timestamp
- **Type**: Optional datetime
- **Purpose**: Track when the system collected/scraped the content
- **Value**: Set to `datetime.utcnow()` when EventData is created
- **Format**: ISO 8601 datetime string
- **Display**: Formatted with date and time (e.g., "December 7, 2025 3:45 PM")
- **Timezone**: UTC

---

## Updated Event Details Modal Field Order

The modal now displays fields in this exact order:

1. Event Time
2. Event Type ✅
3. **Event Sub-Type** ✅ NEW
4. Event Title
5. Event Summary
6. Perpetrator
7. **Perpetrator Type** ✅ NEW
8. Location (Full)
9. City/Town
10. State/Province
11. Country
12. Individuals Involved
13. Organizations Involved
14. Casualties
15. Source Name
16. Source URL
17. Publication Date
18. Event Date
19. Extraction Confidence
20. **Collection Timestamp** ✅ NEW
21. Full Content

---

## Example Event Data (with new fields)

```json
{
  "event_type": "bombing",
  "event_sub_type": "suicide bombing",
  "title": "2023 Kabul airport bombing",
  "summary": "A suicide bombing occurred at a checkpoint outside the military airport in Kabul, Afghanistan on January 1, 2023.",
  "perpetrator": "Islamic State",
  "perpetrator_type": "terrorist_group",
  "location": {
    "city": "Kabul",
    "state": "Kabul Province",
    "country": "Afghanistan"
  },
  "event_date": "2023-01-01T00:00:00Z",
  "event_time": "10:30",
  "organizations": ["Islamic State", "Taliban"],
  "casualties": {
    "killed": 5,
    "injured": 12
  },
  "source_name": "Wikipedia",
  "source_url": "https://en.wikipedia.org/wiki/2023_Kabul_airport_bombing",
  "article_published_date": "2023-01-01T00:00:00Z",
  "collection_timestamp": "2025-12-07T15:30:00Z",
  "confidence": 0.85
}
```

---

## Testing the New Fields

### How to Test:

1. **Backend Auto-Reload**: The backend uses `--reload` flag and should automatically reload
2. **Frontend Running**: Already running on http://localhost:5173

### Test Steps:

1. **Perform a New Search**:
   - Search for: "kabul airport bombing 2023" or similar
   - Wait for LLM extraction to complete

2. **Verify New Fields in Modal**:
   - Click "Details" button on any event
   - Look for new fields:
     - **Event Sub-Type**: Should show if LLM extracted (e.g., "suicide bombing")
     - **Perpetrator Type**: Should show if perpetrator identified (e.g., "Terrorist Group")
     - **Collection Timestamp**: Should ALWAYS show (current UTC time when scraped)

3. **Check Field Formatting**:
   - Event Sub-Type: Plain text
   - Perpetrator Type: Title Case (spaces between words)
   - Collection Timestamp: Formatted date/time

### Expected Results:

✅ **Event Sub-Type**: Shows when LLM extracts specific classification
✅ **Perpetrator Type**: Shows and formatted as "Terrorist Group", "State Actor", etc.
✅ **Collection Timestamp**: Always shows current UTC time when event was extracted

---

## LLM Prompt Changes

### Before:
```
RESPOND WITH VALID JSON ONLY (no markdown, no explanations):
{
    "event_type": "bombing",
    "summary": "...",
    "perpetrator": "Taliban",
    ...
}
```

### After:
```
PERPETRATOR TYPES (choose one if perpetrator identified):
- terrorist_group: Known terrorist organizations
- state_actor: Government or military forces
- criminal_organization: Organized crime groups
- individual: Single person or small group
- multiple_parties: Multiple distinct groups involved
- unknown: Perpetrator not identified
- not_applicable: No perpetrator (e.g., natural disasters)

RESPOND WITH VALID JSON ONLY (no markdown, no explanations):
{
    "event_type": "bombing",
    "event_sub_type": "suicide bombing" or "vehicle bombing" or null,
    "summary": "...",
    "perpetrator": "Islamic State",
    "perpetrator_type": "terrorist_group" or null,
    ...
}
```

---

## Files Modified

### Backend (3 files):
1. ✅ `backend/app/models.py` - Added PerpetratorType enum, updated EventData model
2. ✅ `backend/app/services/event_extractor.py` - Added validation, updated prompt and creation
3. ✅ (Auto-reload) Backend should restart automatically

### Frontend (2 files):
1. ✅ `frontend/src/types/events.ts` - Updated EventData interface
2. ✅ `frontend/src/components/EventDetailsModal.tsx` - Uncommented fields, added formatting

---

## Validation & Error Handling

### Perpetrator Type Validation:
- **Exact Match**: `"terrorist_group"` → `PerpetratorType.TERRORIST_GROUP`
- **Fuzzy Match**: `"Terrorist Group"` → `PerpetratorType.TERRORIST_GROUP`
- **Keyword Match**: `"militant group"` → `PerpetratorType.TERRORIST_GROUP`
- **Unknown**: `"unidentified"` → `PerpetratorType.UNKNOWN`
- **Default**: If can't determine → `PerpetratorType.UNKNOWN`

### Event Sub-Type:
- Free-text field (no validation)
- LLM determines appropriate classification
- Examples in prompt guide LLM

### Collection Timestamp:
- Always set to `datetime.utcnow()` at time of EventData creation
- Never null for new events
- Persists through JSON serialization

---

## Success Criteria

### ✅ Backend Implementation Complete:
- [x] PerpetratorType enum created
- [x] EventData model updated with 3 new fields
- [x] LLM prompt updated with extraction instructions
- [x] Perpetrator type validation function added
- [x] Collection timestamp auto-set on creation
- [x] No compilation errors

### ✅ Frontend Implementation Complete:
- [x] TypeScript interface updated
- [x] Event Details Modal fields uncommented
- [x] Formatting functions added
- [x] No compilation errors

### ✅ Ready for Testing:
- [x] Backend auto-reload enabled
- [x] Frontend dev server running
- [x] All fields properly typed
- [x] Validation logic in place

---

## Next Steps

1. **Test with Real Data**: Perform a search and verify new fields appear
2. **Validate LLM Output**: Check if LLM correctly extracts event_sub_type and perpetrator_type
3. **Verify Timestamps**: Confirm collection_timestamp shows current time
4. **Check Formatting**: Ensure perpetrator_type displays as Title Case

---

## Troubleshooting

### If fields don't appear:

**Event Sub-Type / Perpetrator Type not showing:**
- These are optional fields
- LLM may not always extract them
- Try more specific searches (e.g., "terrorist attack", "suicide bombing")

**Collection Timestamp not showing:**
- Should ALWAYS appear for new events
- Check browser console for errors
- Verify backend response includes `collection_timestamp`

**Perpetrator Type shows as snake_case:**
- Check `formatPerpetratorType()` function is working
- Should convert "terrorist_group" → "Terrorist Group"

---

## API Response Example

When backend sends event data to frontend:

```json
{
  "event_data": {
    "event_type": "bombing",
    "event_sub_type": "suicide bombing",
    "perpetrator_type": "terrorist_group",
    "collection_timestamp": "2025-12-07T15:30:00.000Z",
    ...
  }
}
```

Frontend receives and displays:
- **Event Sub-Type**: "suicide bombing"
- **Perpetrator Type**: "Terrorist Group" (formatted)
- **Collection Timestamp**: "December 7th, 2025 3:30 PM" (formatted)

---

## Documentation Updates

Updated documentation files:
- ✅ `doc/EventDetailsModal_FieldSpecification.md` - Now reflects backend implementation
- ✅ `doc/EventDetailsModal_UpdateSummary.md` - Marked fields as implemented
- ✅ This file: Complete implementation summary

---

## Status: ✅ IMPLEMENTATION COMPLETE

All 3 requested fields are now fully implemented in both backend and frontend:
1. ✅ Event Sub-Type
2. ✅ Perpetrator Type
3. ✅ Collection Timestamp

**Ready for testing with real search queries!**
