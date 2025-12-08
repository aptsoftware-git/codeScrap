# Event Details Modal - Update Summary

## Changes Made (December 7, 2025)

### ✅ Updated Field Order
Reorganized Event Details modal to match your exact requirements:

1. **Event Time** (if available)
2. **Event Type** (color-coded chip)
3. **Event Title**
4. **Event Summary**
5. **Perpetrator**
6. **Location (Full)** (combined: venue, city, state, country)
7. **City/Town** (if available)
8. **State/Province** (if available)
9. **Country** (if available)
10. **Individuals Involved** (renamed from "Participants")
11. **Organizations Involved** (renamed from "Organizations")
12. **Casualties** (killed + injured chips)
13. **Source Name** (if available)
14. **Source URL** (clickable link)
15. **Publication Date** (renamed from "Article Published")
16. **Event Date**
17. **Extraction Confidence** (renamed from "Confidence Score", %)
18. **Full Content** (scrollable box)

---

### ❌ Removed Fields

**Impact** - Removed as requested
- Reason: Duplicate of Event Summary
- User feedback: "Impact is not required as it is same as event title"

**Relevance Score** - Moved to event card only
- Not part of core event data
- Still shown on event cards as chip

---

### ⏳ Fields Pending Backend Implementation

The following fields are **commented out** in the code until backend support is added:

1. **Event Sub-Type** - Secondary classification
   - Needs: Backend field + LLM extraction logic
   - Example: "suicide bombing", "mass shooting"

2. **Perpetrator Type** - Classification
   - Needs: Backend field + categorization logic
   - Example: "Terrorist Group", "State Actor", "Unknown"

3. **Collection Timestamp** - When system retrieved content
   - Needs: Backend field (capture scrape time)
   - Example: "December 7, 2025 3:45 PM UTC"

---

## Files Modified

### `frontend/src/components/EventDetailsModal.tsx`
**Changes**:
- Reordered all fields to match requirements
- Renamed headings:
  - "Participants" → "Individuals Involved"
  - "Organizations" → "Organizations Involved"
  - "Article Published" → "Publication Date"
  - "Confidence Score" → "Extraction Confidence"
- Removed "Impact" field display
- Removed "Relevance Score" from modal
- Split location into: Full, City/Town, State/Province, Country
- Changed "Individuals/Organizations" from chips to comma-separated text
- Increased left column width to 35% for longer labels
- Commented out missing fields (Event Sub-Type, Perpetrator Type, Collection Timestamp)

---

## Testing the Changes

### How to Test:
1. Frontend is running on http://localhost:5173
2. Backend should be running on http://localhost:8000
3. Perform a search to get events
4. Click "Details" button on any event card
5. Verify field order matches specification

### Expected Results:
✅ Fields appear in the exact order specified
✅ "Individuals Involved" and "Organizations Involved" show as comma-separated text
✅ Location split into 4 rows (Full, City, State, Country)
✅ "Impact" field not displayed
✅ "Publication Date" and "Extraction Confidence" have new labels
✅ All fields properly formatted

---

## Example Output (Your Kabul Event)

Based on your example, the modal should display:

```
Event Time:              N/A (not in your data)
Event Type:              [bombing] (red chip)
Event Title:             2023 Kabul airport bombing
Event Summary:           A bombing occurred at a checkpoint outside 
                         the military airport in Kabul, Afghanistan 
                         on January 1, 2023.
Perpetrator:             N/A
Location (Full):         Kabul, Afghanistan
City/Town:               Kabul
Country:                 Afghanistan
Individuals Involved:    (not shown - empty)
Organizations Involved:  Islamic State, Taliban
Casualties:              [Killed: 5] [Injured: 12]
Source Name:             DuckDuckGo
Source URL:              https://en.wikipedia.org/wiki/2023_Kabul_airport_bombing
Publication Date:        January 1st, 2023 12:00 AM
Event Date:              January 1st, 2023 12:00 AM
Extraction Confidence:   [85%] (green chip)
Full Content:            [Scrollable box with Wikipedia text]
```

**Note**: Your example shows some parsing issues in the LLM output:
- Organizations field contains: "Islamic State", "Taliban", "Afghanistanis", "International AirportinAfghanistankilled", "Wikipedia"
- This suggests the LLM prompt needs refinement to extract cleaner organization names

---

## Questions for Implementation

To implement the missing fields, please clarify:

### 1. Event Sub-Type
- **Option A**: Free-text field (LLM decides)
  - Pro: Flexible, captures nuance
  - Con: Inconsistent categories
- **Option B**: Predefined enum
  - Examples: "Suicide Bombing", "Vehicle Attack", "Mass Shooting", "Stabbing", "Arson"
  - Pro: Consistent, filterable
  - Con: Might miss edge cases
- **Your preference?**

### 2. Perpetrator Type
- **Suggested categories**:
  - Terrorist Group
  - State Actor
  - Criminal Organization
  - Individual
  - Multiple Parties
  - Unknown
- **Should LLM classify or use rule-based matching?**
- **Any additional categories needed?**

### 3. Collection Timestamp
- **When to capture**:
  - When article is scraped from web
  - When LLM processes the article
  - When event is saved to session
- **Timezone**: UTC or local?
- **Your preference?**

---

## Status

**Current Status**: ✅ READY FOR TESTING

**Frontend**: Running on http://localhost:5173
**Backend**: Running on http://localhost:8000

**Next Steps**:
1. Test the updated modal with real search results
2. Verify field order and labels match requirements
3. Provide feedback on missing fields (Event Sub-Type, Perpetrator Type, Collection Timestamp)
4. I'll implement backend support for missing fields based on your specifications

---

## Related Documentation

- `doc/EventDetailsModal_FieldSpecification.md` - Complete field specification
- `doc/UI_Improvements_Summary.md` - Original changes summary
- `doc/Testing_Guide_UI_Improvements.md` - Testing instructions
